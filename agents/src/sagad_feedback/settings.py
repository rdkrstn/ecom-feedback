from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


PACKAGE_DIR = Path(__file__).resolve().parent
AGENTS_DIR = PACKAGE_DIR.parents[1]
DATA_DIR = AGENTS_DIR / "data"
DEFAULT_DB_PATH = DATA_DIR / "reviews.db"


def load_environment() -> None:
    load_dotenv(AGENTS_DIR / ".env")
    load_dotenv()


def get_public_api_url() -> str:
    load_environment()
    return os.getenv("PUBLIC_API_URL", "http://localhost:8000").rstrip("/")


def get_api_base_url() -> str:
    return get_public_api_url()
