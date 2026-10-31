import bcrypt
import streamlit as st

from src.db import get_user


def hash_password(password):
    """Turn a password into a bcrypt hash. The plain password is never stored."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password, password_hash):
    """True if the password matches the stored hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def login(username, password):
    """Check credentials. On success, remember the user in the session."""
    user = get_user(username.strip().lower())
    if user and check_password(password, user["password_hash"]):
        st.session_state["user"] = {
            "username": user["username"],
            "role": user["role"],
            "full_name": user["full_name"],
            "student_row": user["student_row"],
        }
        return True
    return False


def logout():
    st.session_state.pop("user", None)


def current_user():
    return st.session_state.get("user")


def require_role(*allowed_roles):
    """Call at the top of a page. Stops the page if the user may not see it."""
    user = current_user()
    if user is None:
        st.warning("Please log in on the Home page first.")
        st.stop()
    if user["role"] not in allowed_roles:
        st.error("Access denied: your role cannot open this page.")
        st.stop()
    return user