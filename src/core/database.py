import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Base

load_dotenv('src/cfg/.env')

DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

DB_URL = f"postgresql+psycopg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# DB_URL = "sqlite:///db/example_with_posts.db"
os.makedirs('db/', exist_ok=True)
engine = create_engine(
    url=DB_URL,
    # echo=True,
    isolation_level='SERIALIZABLE'
)

Session = sessionmaker(engine)


def create_tables():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
