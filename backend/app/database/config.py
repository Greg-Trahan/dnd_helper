
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL

# Locate the project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")


def get_database_url():
    """Build the PostgreSQL connection URL."""

    required = [
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
    ]

    missing = [key for key in required if not os.getenv(key)]

    if missing:
        raise RuntimeError(
            f"Missing database environment variables: {', '.join(missing)}"
        )

    return URL.create(
        drivername="postgresql+psycopg",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        database=os.getenv("DB_NAME"),
    )
