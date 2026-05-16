from app.database import SessionLocal
from app.models import User
from app.auth import hash_password


db = SessionLocal()

admin = User(
    username="admin",
    password=hash_password("admin123"),
    role="admin"
)


db.add(admin)

db.commit()

print("Admin created")
