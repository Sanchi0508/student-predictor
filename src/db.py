import psycopg
import streamlit as st


def get_conn():
    """Open a connection to the Neon database using the saved secret."""
    return psycopg.connect(st.secrets["DATABASE_URL"])


def init_db():
    """Create the tables if they do not exist yet."""
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            SERIAL PRIMARY KEY,
                username      TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role          TEXT NOT NULL
                              CHECK (role IN ('student', 'teacher', 'admin')),
                full_name     TEXT NOT NULL,
                student_row   INTEGER,
                created_at    TIMESTAMP DEFAULT NOW()
            )
        """)


def create_user(username, password_hash, role, full_name, student_row=None):
    """Add a user. Returns False if the username is already taken."""
    try:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash, role, full_name, student_row) "
                "VALUES (%s, %s, %s, %s, %s)",
                (username, password_hash, role, full_name, student_row),
            )
        return True
    except psycopg.errors.UniqueViolation:
        return False


def get_user(username):
    """Return one user as a dict, or None if not found."""
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT id, username, password_hash, role, full_name, student_row "
            "FROM users WHERE username = %s",
            (username,),
        )
        r = cur.fetchone()
    if r is None:
        return None
    keys = ["id", "username", "password_hash", "role", "full_name", "student_row"]
    return dict(zip(keys, r))


def list_users():
    """All users without their password hashes (for the admin page)."""
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT username, role, full_name, created_at FROM users ORDER BY id"
        )
        return cur.fetchall()