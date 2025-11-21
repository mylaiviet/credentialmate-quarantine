import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine

with engine.connect() as conn:
    try:
        result = conn.execute(text("SELECT version_num FROM alembic_version"))
        versions = list(result)
        print(f"Current version: {versions}")
    except Exception as e:
        print(f"Error or no alembic_version table: {e}")
