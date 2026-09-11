# =========================================================
# Database Configuration
# =========================================================

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# =========================================================
# SQLite database
# =========================================================

DATABASE_URL = "sqlite:///./documents.db"


# =========================================================
# Create database engine
# =========================================================

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)


# =========================================================
# Database session
# =========================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# =========================================================
# Base class for database models
# =========================================================

Base = declarative_base()


# =========================================================
# Get database session
# =========================================================

def get_db():
    """
    Create a database session for an API request.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()