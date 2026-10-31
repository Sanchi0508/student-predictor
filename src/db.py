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

def init_interventions():
    """Create the interventions table if it does not exist yet."""
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS interventions (
                id             SERIAL PRIMARY KEY,
                student_row    INTEGER NOT NULL,
                action         TEXT NOT NULL,
                notes          TEXT,
                status         TEXT NOT NULL DEFAULT 'open'
                               CHECK (status IN ('open', 'in_progress', 'done')),
                follow_up_date DATE,
                created_by     TEXT NOT NULL,
                created_at     TIMESTAMP DEFAULT NOW()
            )
        """)


def add_intervention(student_row, action, notes, follow_up_date, created_by):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO interventions "
            "(student_row, action, notes, follow_up_date, created_by) "
            "VALUES (%s, %s, %s, %s, %s)",
            (student_row, action, notes, follow_up_date, created_by),
        )


def list_interventions(student_row=None):
    """All interventions, newest first. Optionally only for one student row."""
    sql = ("SELECT id, student_row, action, notes, status, follow_up_date, "
           "created_by, created_at FROM interventions")
    params = ()
    if student_row is not None:
        sql += " WHERE student_row = %s"
        params = (student_row,)
    sql += " ORDER BY created_at DESC"
    with get_conn() as conn:
        return conn.execute(sql, params).fetchall()


def update_intervention_status(intervention_id, status):
    with get_conn() as conn:
        conn.execute(
            "UPDATE interventions SET status = %s WHERE id = %s",
            (status, intervention_id),
        )