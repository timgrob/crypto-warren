from sqlalchemy.orm import Session, sessionmaker, declarative_base
from sqlalchemy import create_engine
from typing import Generator
import os


DATABASE_URL = os.getenv("DB_URL")
print(DATABASE_URL)

Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
