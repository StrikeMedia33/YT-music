"""
Database Connection and Session Management
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please add it to your .env file."
    )

# Create SQLAlchemy engine
# Use NullPool for serverless environments (Neon Postgres works well with this)
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # No connection pooling (good for serverless)
    echo=False,  # Set to True for SQL query logging during development
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


def get_db():
    """
    Dependency function for FastAPI routes
    Provides a database session and ensures it's closed after use

    Usage in FastAPI:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database (create all tables)

    Note: In production, use migrations instead of this
    This is mainly for testing and development
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")


def drop_all_tables():
    """
    Drop all tables (development only!)
    WARNING: This will delete all data
    """
    Base.metadata.drop_all(bind=engine)
    print("⚠️  All tables dropped")
