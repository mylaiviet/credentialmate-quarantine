"""Drop and recreate the database schema"""
from sqlalchemy import create_engine, text
from app.core.config import settings


def reset_database():
    engine = create_engine(settings.database_url)

    with engine.connect() as conn:
        # Drop everything
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        conn.commit()
        print("✓ Database schema reset successfully")


if __name__ == "__main__":
    reset_database()
