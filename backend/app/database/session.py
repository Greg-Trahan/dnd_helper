
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.config import get_database_url

# Create the database engine
engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,
    echo=False,
)

# Create database sessions
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)
