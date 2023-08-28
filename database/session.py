from config import settings
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

__session = sessionmaker(bind=create_engine(
    settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True), autoflush=False, autocommit=False)


def get_sesston() -> Generator:
    try:
        db = __session()
        yield db
    finally:
        db.close()
