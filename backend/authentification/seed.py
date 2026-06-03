"""
Script to seed the database with test users
"""
import sys
from pathlib import Path
import hashlib

# Add app directory to path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

from app.database import Base, engine, SessionLocal
from app.model import UserDB

def simple_hash(password: str) -> str:
    """Simple password hash using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def seed_database():
    """Create tables and insert test users"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if users already exist
        existing_users = db.query(UserDB).count()
        if existing_users > 0:
            print("✓ Users already exist in database")
            return
        
        # Create test users
        users = [
            UserDB(
                identifiant="yahya_dev",
                email="yahya@example.com",
                mot_de_passe_hache=simple_hash("password123"),
                role="analyste_senior",
                is_active=True
            ),
            UserDB(
                identifiant="admin",
                email="admin@example.com",
                mot_de_passe_hache=simple_hash("admin123"),
                role="admin",
                is_active=True
            ),
            UserDB(
                identifiant="analyste",
                email="analyste@example.com",
                mot_de_passe_hache=simple_hash("analyste123"),
                role="analyste",
                is_active=True
            ),
        ]
        
        db.add_all(users)
        db.commit()
        
        print("✓ Database seeded successfully!")
        print("\nTest Users Created:")
        print("─" * 50)
        for user in users:
            print(f"  • ID: {user.identifiant:20} Password: password123")
        print("─" * 50)
        
    except Exception as e:
        print(f"✗ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
