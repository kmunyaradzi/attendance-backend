import os
import sys

from dotenv import load_dotenv

from app.core.security import hash_password
from app.db import SessionLocal
from app.models.user import User

load_dotenv()

email = os.getenv("SUPER_ADMIN_EMAIL")
password = os.getenv("SUPER_ADMIN_PASSWORD")

if not email or not password:
    print("ERROR: SUPER_ADMIN_EMAIL and SUPER_ADMIN_PASSWORD must be set in .env")
    sys.exit(1)

db = SessionLocal()
try:
    user = db.query(User).filter_by(email=email).first()
    if user:
        print("Super admin already exists")
        sys.exit(0)

    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name="Super Admin",
        role="super_admin",
        is_active=True,
    )
    db.add(user)
    db.commit()
    print(f"Super admin created: {email}")
finally:
    db.close()
