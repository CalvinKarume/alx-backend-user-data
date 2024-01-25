#!/usr/bin/env python3
"""
Authentication and User Management Module
"""

import bcrypt
from uuid import uuid4
from sqlalchemy.orm.exc import NoResultFound
from typing import TypeVar, Union

from db import DB
from user import User

U = TypeVar(User)


def _hash_password(password: str) -> bytes:
    """
    Hashes a password string using a secure algorithm and returns the hashed password as bytes.
    Args:
        password (str): The user's password in string format.
    """
    passwd = password.encode('utf-8')
    return bcrypt.hashpw(passwd, bcrypt.gensalt())


def _generate_uuid() -> str:
    """
    Generates a unique identifier (UUID) and returns its string representation.
    """
    return str(uuid4())


class UserAuthentication:
    """User Authentication and Management Class
    """

    def __init__(self) -> None:
        """
        Initializes the User Authentication and Management instance.
        """
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """
        Registers a new user, securely hashes the password, and returns the user object.
        Args:
            email (str): The new user's email address.
            password (str): The new user's password.
        Return:
            If no user with the given email exists, returns the newly created user.
            Otherwise, raises a ValueError.
        """
        try:
            self._db.find_user_by(email=email)
        except NoResultFound:
            hashed = _hash_password(password)
            new_user = self._db.add_user(email, hashed)
            return new_user
        raise ValueError(f"User {email} already exists")

    def valid_login(self, email: str, password: str) -> bool:
        """
        Validates a user's login credentials and returns True if they are correct, or False if they are not.
        Args:
            email (str): The user's email address.
            password (str): The user's password.
        Return:
            True if credentials are correct, else False.
        """
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            return False

        user_password = user.hashed_password
        passwd = password.encode("utf-8")
        return bcrypt.checkpw(passwd, user_password)

