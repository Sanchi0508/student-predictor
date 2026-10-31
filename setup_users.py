

from src.auth import hash_password
from src.db import create_user, init_db, list_users

init_db()
print("Table 'users' is ready.\n")

accounts = [
    ("admin1",   "admin",   "Admin (HOD)",   None),
    ("teacher1", "teacher", "Teacher One",   None),
    ("student1", "student", "Student One",   0),   # linked to row 0 of the dataset
]

for username, role, full_name, student_row in accounts:
    pw = input(f"Choose a password for {username} ({role}): ")
    if len(pw) < 6:
        print("  Too short (minimum 6 characters). Skipped.")
        continue
    ok = create_user(username, hash_password(pw), role, full_name, student_row)
    print("  Created." if ok else "  Already exists, skipped.")

print("\nUsers in the database:")
for row in list_users():
    print(" ", row[0], "|", row[1], "|", row[2])