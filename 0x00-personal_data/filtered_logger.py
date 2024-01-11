#!/usr/bin/env python3
"""
Logging and Data Filtering Module
"""

import logging
import re
from typing import List
import os
import mysql.connector

PII_FIELDS = ("name", "email", "ssn", "phone", "address")


def filter_log_data(fields: List[str], redaction: str,
                    message: str, separator: str) -> str:
    """
    Obfuscate specified fields in a log message.

    Args:
        fields (List[str]): List of fields to obfuscate.
        redaction (str): String representing how the field will be obfuscated.
        message (str): Log line.
        separator (str): Character separating all fields in the log line.

    Returns:
        str: Obfuscated log message.
    """
    regex = f'({separator}|^)({"|".join(fields)}=.+?)(?={separator}|$)'
    return re.sub(regex, f'\\1{redaction}', message)


class LogRedactingFormatter(logging.Formatter):
    """
    Custom Log Redacting Formatter class
    """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields=None):
        """
        Initialize LogRedactingFormatter class.

        Args:
            fields (List[str]): List of fields to redact.
        """
        super(LogRedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log records with redacted fields.

        Args:
            record (logging.LogRecord): Log record to be formatted.

        Returns:
            str: Formatted log message.
        """
        if self.fields:
            for field in self.fields:
                record.msg = re.sub(f'{field}=.+?;',
                                    f'{field}={self.REDACTION};', record.msg)
        return super(LogRedactingFormatter, self).format(record)


def get_data_logger() -> logging.Logger:
    """
    Return a configured data logger.

    Returns:
        logging.Logger: Logger object for handling data logs.
    """
    logger = logging.getLogger('user_data')
    logger.setLevel(logging.INFO)
    logger.propagate = False
    stream_handler = logging.StreamHandler()
    formatter = LogRedactingFormatter(PII_FIELDS)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger


def get_database_connector() -> mysql.connector.connection.MySQLConnection:
    """
    Return a connector to the database.

    Returns:
        mysql.connector.connection.MySQLConnection: Database connector.
    """
    connector = mysql.connector.connect(
        user=os.environ.get('PERSONAL_DATA_DB_USERNAME', 'root'),
        password=os.environ.get('PERSONAL_DATA_DB_PASSWORD', ''),
        host=os.environ.get('PERSONAL_DATA_DB_HOST', 'localhost'),
        database=os.environ.get('PERSONAL_DATA_DB_NAME'))
    return connector


def main():
    """
    Retrieve and filter data from the database and log it.
    """
    db = get_database_connector()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users;")
    logger = get_data_logger()
    for row in cursor:
        log_msg = ' '.join([f"{key}={row[key]}" for key in row])
        logger.info(log_msg)
    cursor.close()
    db.close()


if __name__ == '__main__':
    main()

