#!/usr/bin/env python3
"""
SessionExpAuth Module

This module defines the SessionExpAuth class, which extends SessionAuth
and adds an expiration date to a Session ID.
"""

import os
from datetime import datetime, timedelta
from .session_auth import SessionAuth


class SessionExpAuth(SessionAuth):
    """
    SessionExpAuth Class

    A class that extends SessionAuth and adds an expiration date to a Session ID.
    """

    def __init__(self):
        """
        Initialize the SessionExpAuth class.

        Reads the SESSION_DURATION environment variable and sets the session_duration
        attribute accordingly. If the environment variable is not set or an error
        occurs during conversion, the session_duration is set to 0 (no expiration).
        """
        try:
            duration = int(os.getenv('SESSION_DURATION'))
        except Exception:
            duration = 0
        self.session_duration = duration

    def create_session(self, user_id=None):
        """
        Create Session ID for a user.

        Args:
            user_id (str): User ID for which the session is created.

        Returns:
            str: Session ID if created successfully, otherwise None.
        """
        session_id = super().create_session(user_id)
        if session_id is None:
            return None
        session_dictionary = {
            "user_id": user_id,
            "created_at": datetime.now()
        }
        self.user_id_by_session_id[session_id] = session_dictionary
        return session_id

    def user_id_for_session_id(self, session_id=None):
        """
        Retrieve user ID based on a session ID.

        Args:
            session_id (str): Session ID to look up.

        Returns:
            str: User ID if the session is valid and not expired, otherwise None.
        """
        if session_id is None:
            return None
        user_details = self.user_id_by_session_id.get(session_id)
        if user_details is None or "created_at" not in user_details:
            return None

        if self.session_duration <= 0:
            return user_details.get("user_id")

        created_at = user_details.get("created_at")
        allowed_window = created_at + timedelta(seconds=self.session_duration)

        if allowed_window < datetime.now():
            return None
        return user_details.get("user_id")

