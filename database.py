# database.py
# This file handles ALL communication with the SQLite database.
# It manages two tables: 'users' (for login/signup) and 'students' (for records).

import sqlite3
import hashlib

DB_NAME = "school.db"


def get_connection():
    """Opens a connection to our SQLite database file."""
    conn = sqlite3.connect(DB_NAME)
    return conn


def hash_password(password):
    """
    Converts a plain password into a scrambled 'hash' before saving it.
    We NEVER store real passwords in the database — if the database
    were ever leaked, hashed passwords can't easily be reversed back
    into the original password.
    """
    return hashlib.sha256(password.encode()).hexdigest()


def create_tables():
    """Creates 'users' and 'students' tables if they don't already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    name TEXT NOT NULL,
    roll_no TEXT NOT NULL,
    subject1 REAL NOT NULL,
    subject2 REAL NOT NULL,
    subject3 REAL NOT NULL,
    total REAL NOT NULL,
    percentage REAL NOT NULL,
    grade TEXT NOT NULL,
    result TEXT NOT NULL
)
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# USER ACCOUNT FUNCTIONS
# ---------------------------------------------------------

def create_user(username, password):
    """
    Creates a new user account. Returns True on success,
    False if the username is already taken.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # This error happens automatically if 'username' already exists,
        # because we marked it UNIQUE in the table definition above.
        return False
    finally:
        conn.close()


def verify_user(username, password):
    """
    Checks if a username/password combination is correct.
    Returns True if valid, False otherwise.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return False  # username doesn't exist

    stored_hash = row[0]
    return stored_hash == hash_password(password)


# ---------------------------------------------------------
# STUDENT FUNCTIONS (same as before)
# ---------------------------------------------------------

def add_student(username, name, roll_no, subject1, subject2, subject3,
                total, percentage, grade, result):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO students
        (username,name,roll_no,subject1,subject2,subject3,total,percentage,grade,result)

        VALUES(?,?,?,?,?,?,?,?,?,?)
    """,(username,name,roll_no,subject1,subject2,
         subject3,total,percentage,grade,result))

    conn.commit()
    conn.close()
  


def get_all_students(username):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE username=?",
        (username,)
    )

    rows = cursor.fetchall()

    conn.close()
    return rows


def update_student(student_id, name, roll_no, subject1, subject2, subject3, total, percentage, grade, result):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE students
        SET name=?, roll_no=?, subject1=?, subject2=?, subject3=?,
            total=?, percentage=?, grade=?, result=?
        WHERE id=?
    """, (name, roll_no, subject1, subject2, subject3, total, percentage, grade, result, student_id))
    conn.commit()
    conn.close()


def delete_student(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    conn.close()

def search_student(username, keyword):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM students
        WHERE username=?
        AND (name LIKE ? OR roll_no LIKE ?)
    """,
    (
        username,
        f"%{keyword}%",
        f"%{keyword}%"
    ))

    rows = cursor.fetchall()

    conn.close()
    return rows
