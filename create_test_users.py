import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
import uuid
from datetime import UTC, datetime

# Import your models
from app.models.user_model import User
from app.config import settings

# Create database connection
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Role definitions
ROLES = [
    
    {
        "id": "12c9a3ee-6ea8-4f7b-9ec3-b64e5177651f",
        "name": "finance"
    },
    {
        "id": "ed2e3c7e-98df-4e20-8dce-e0dd127642db",
        "name": "auditor"
    },
    {
        "id": "094f40bd-14de-48b0-8979-c8a7da41cab2",
        "name": "client"
    }
]

def create_admin_user():
    try:
        # Admin role ID
        admin_role_id = "81abbed1-a608-4a37-ac3a-e7de1ec80944"
        
        # Create admin user with known password
        password = "admin123"
        hashed_password = pwd_context.hash(password)
        
        admin_user = User(
            id=uuid.uuid4(),
            username="admin",
            email="admin@admin.com",
            password_hash=hashed_password,
            role_id=admin_role_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"\nAdmin user created successfully!")
        print(f"Username: admin")
        print(f"Password: admin123")
        print(f"User ID: {admin_user.id}")
        print(f"Role: admin (ID: {admin_role_id})")
        print(f"Hashed password: {hashed_password}")
        
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
        db.rollback()
    finally:
        db.close()

def create_test_users():
    try:
        for role in ROLES:
            # Create test user with hashed password
            username = f"test_{role['name']}"
            email = f"{role['name']}@admin.com"
            test_password = f"test{role['name']}123"  # e.g., testadmin123, testfinance123
            hashed_password = pwd_context.hash(test_password)
            
            test_user = User(
                id=uuid.uuid4(),
                username=username,
                email=email,
                password_hash=hashed_password,
                role_id=role['id'],
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )
            
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            
            print(f"\nTest {role['name']} user created successfully!")
            print(f"Username: {username}")
            print(f"Password: {test_password}")
            print(f"User ID: {test_user.id}")
            print(f"Role: {role['name']} (ID: {role['id']})")
            
    except Exception as e:
        print(f"Error creating test users: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()