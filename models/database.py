import sqlite3
import os
from datetime import datetime

DATABASE_NAME = 'weather_data.db'

def get_db_connection():
    # Get database connection
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def check_db_connection():
    # Check if database connection is working
    try:
        conn = get_db_connection()
        conn.execute('SELECT 1')
        conn.close()
        return True
    except Exception as e:
        print(f"Database connection check failed: {e}")
        return False

def init_db():
    # Initialize the database with weather_data table
    conn = get_db_connection()
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS weather_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                temperature_2m REAL NOT NULL,
                relative_humidity_2m REAL NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

def insert_weather_data(data_list):
    # Insert weather data into the database - data_list: List of tuples containing weather data
    conn = get_db_connection()
    try:
        cursor = conn.cursor()  # Create cursor object
        cursor.executemany('''
            INSERT INTO weather_data (timestamp, latitude, longitude, temperature_2m, relative_humidity_2m)
            VALUES (?, ?, ?, ?, ?)
        ''', data_list)
        conn.commit()
        return cursor.rowcount  # Return number of affected rows instead of lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_last_48_hours_data():
    # Get weather data from the last 48 hours
    conn = get_db_connection()
    try:
        cursor = conn.execute('''
            SELECT timestamp, latitude, longitude, temperature_2m, relative_humidity_2m
            FROM weather_data
            WHERE datetime(timestamp) >= datetime('now', '-2 days')
            ORDER BY timestamp DESC
        ''')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        raise e
    finally:
        conn.close()

def get_all_weather_data():
    # Get all weather data from database
    conn = get_db_connection()
    try:
        cursor = conn.execute('''
            SELECT timestamp, latitude, longitude, temperature_2m, relative_humidity_2m
            FROM weather_data
            ORDER BY timestamp DESC
        ''')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        raise e
    finally:
        conn.close()
