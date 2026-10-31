from src.auth import check_password, hash_password
from src.db import get_conn, get_user

NEW_PASSWORD = "Admin@2026"

with get_conn() as conn:
    conn.execute(
        "INSERT INTO users (username, password_hash, role, full_name) "
        "VALUES (%s, %s, %s, %s) "
        "ON CONFLICT (username) DO UPDATE SET "
        "password_hash = EXCLUDED.password_hash, role = 'admin'",
        ("admin1", hash_password(NEW_PASSWORD), "admin", "Admin (HOD)"),
    )

u = get_user("admin1")
print("admin1 found:", u is not None)
print("role:", u["role"])
print("password check:", check_password(NEW_PASSWORD, u["password_hash"]))