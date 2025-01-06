import os
from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

# MongoDB 설정
password = quote_plus(os.environ['MONGO_PW'])
MONGO_URI = f"mongodb+srv://jeongbeenson19:{password}@aqua.wchta.mongodb.net/?retryWrites=true&w=majority&appName=aqua"
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client['quiz_db']

# MySQL 설정
my_password = os.environ['MYSQL_PW']
DATABASE_URL = f"mysql+mysqlconnector://root:{my_password}@localhost/user_db"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
