"""Configuration loaded from environment variables.
Checking to see if the PR Auto updates to this new commit."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT : Path = Path(__file__).resolve().parent.parent.parent

_db_path_str: str = os.getenv("DATABASE_PATH", "./knowledge.db")
DATABASE_PATH: Path = (PROJECT_ROOT / _db_path_str).resolve()

LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()