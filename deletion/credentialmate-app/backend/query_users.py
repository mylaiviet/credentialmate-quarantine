"""
Query script to retrieve user information from the database.
"""

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import User, License

# Create database connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # Query all users with license count
    users = db.query(
        User.id,
        User.email,
        User.hashed_password,
        User.first_name,
        User.last_name,
        User.created_at,
        func.count(func.distinct(License.state)).label('num_states_licensed')
    ).outerjoin(
        License, User.id == License.user_id
    ).group_by(
        User.id,
        User.email,
        User.hashed_password,
        User.first_name,
        User.last_name,
        User.created_at
    ).order_by(User.created_at).all()

    if not users:
        print("No users found in the database.")
    else:
        print("\n" + "="*100)
        print("USER INFORMATION FROM DATABASE")
        print("="*100 + "\n")

        for user in users:
            user_id, email, hashed_password, first_name, last_name, created_at, num_states = user
            print(f"User ID:           {user_id}")
            print(f"Email:             {email}")
            print(f"Name:              {first_name} {last_name}")
            print(f"Hashed Password:   {hashed_password}")
            print(f"States Licensed:   {num_states if num_states else 0}")
            print(f"Created At:        {created_at}")
            print("-" * 100)

finally:
    db.close()