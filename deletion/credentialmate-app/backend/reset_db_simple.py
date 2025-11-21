"""Drop and recreate the database schema"""
from sqlalchemy import create_engine, text

DATABASE_URL = (
    "postgresql://credentialmate:dev_password_123@localhost:5435/credentialmate_dev"
)


def reset_database():
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        # Drop everything
        print("Dropping schema...")
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        conn.commit()
        print("SUCCESS: Database schema reset successfully")


if __name__ == "__main__":
    reset_database()
