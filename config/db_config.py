"""
db_config.py
------------
Central place for MySQL connection settings.
Change the values below to match YOUR local MySQL setup.
"""

import mysql.connector
from mysql.connector import Error


# ---------------------------------------------------------------------
# 1. EDIT THESE VALUES to match your MySQL installation
# ---------------------------------------------------------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",          
    "password": "root",          
    "database": "restaurant_management"
}


def get_db_connection():
    """
    Creates and returns a new MySQL connection.
    Every route that needs the database calls this function,
    uses the connection, and then closes it.
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print("❌ Database connection failed:", e)
        return None
