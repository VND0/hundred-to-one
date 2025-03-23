from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base

DB_PATH = "sqlite:///hundred-to-one/database.db"
engine = create_engine(DB_PATH)
Session = sessionmaker(autoflush=False, bind=engine)


def create_db_and_tables():
    Base.metadata.create_all(engine)
