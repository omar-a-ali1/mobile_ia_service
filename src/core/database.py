import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

database_url = os.environ.get("DATABASE_URL")

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()