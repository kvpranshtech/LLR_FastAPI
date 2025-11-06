# fastapi_app/database.py
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base

# PostgreSQL connection (same as Django)
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"

# Engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for ORM
Base = declarative_base()

# ✅ SQLAlchemy 2.x style reflection
metadata = MetaData()
metadata.reflect(bind=engine)
