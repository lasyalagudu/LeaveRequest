# app/core/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

# Engine
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# Session
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Declarative Base
class Base(DeclarativeBase):
    pass

# Depends helper
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize tables
def init_db():
    import app.models  # noqa: F401 (register models)
    Base.metadata.create_all(bind=engine)
