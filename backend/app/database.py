import os
from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# MongoDB 설정
MONGO_URI = 'mongodb://localhost:27017'
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client['quiz_db']

# MySQL 설정
my_password = os.environ['MYSQL_PW']
DATABASE_URL = f"mysql+mysqlconnector://root:{my_password}@localhost/user_db"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
