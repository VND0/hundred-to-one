from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_PATH = "sqlite:///hundred-to-one/data.db"
engine = create_engine(DB_PATH)
Session = sessionmaker(autoflush=False, bind=engine)
