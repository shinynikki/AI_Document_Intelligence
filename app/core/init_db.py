# =========================================================
# Database Initialization
# =========================================================

from app.core.database import Base, engine

# Import the model so SQLAlchemy knows about the table.
from app.models.document import Document


def create_tables():
    """
    Create all database tables if they do not already exist.
    """

    Base.metadata.create_all(
        bind=engine
    )


if __name__ == "__main__":

    create_tables()

    print(
        "Database tables created successfully."
    )