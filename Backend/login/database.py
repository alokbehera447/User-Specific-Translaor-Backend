from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
# only for dev
#from dotenv import load_dotenv
#load_dotenv()

#NOTE remove default behaviour and put all of them in the env variable for better sercurity
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
SQLALCHEMY_DATABASE_URL = f'postgresql://admin_ritik:admin_123@localhost:5434/translator'
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
