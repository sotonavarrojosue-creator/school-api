"""Configuración de base de datos SQLite con SQLAlchemy 2.0."""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./school.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)


def init_db():
    """Crea todas las tablas si no existen."""
    Base.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
