from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DB_PATH = "sqlite:///database/database.db"
engine = create_engine(DB_PATH)
Session = sessionmaker(autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def session_generator():
    while True:
        with Session() as session:
            yield session


def create_db_and_tables():
    Base.metadata.create_all(engine)
