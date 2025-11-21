"""Run Alembic migrations with proper environment setup"""
import os
import sys
from pathlib import Path

# Set working directory to backend folder
backend_dir = Path(__file__).parent
os.chdir(backend_dir)

# Load environment variables from .env
from dotenv import load_dotenv

load_dotenv()

# Now run alembic
from alembic.config import Config
from alembic import command

alembic_cfg = Config("alembic.ini")
command.upgrade(alembic_cfg, "head")
print("SUCCESS: All migrations applied")
