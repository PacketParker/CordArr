from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

if not os.path.exists("data"):
    os.makedirs("data")

database_url = "sqlite:///data/cordarr.db"

engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
Base = declarative_base()
