import json
import os
from pymongo import MongoClient
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

# MongoDB 설정
password = quote_plus(os.getenv('MONGO_PW'))
MONGO_URI = f"mongodb+srv://jeongbeenson19:{password}@aqua.wchta.mongodb.net/?retryWrites=true&w=majority&appName=aqua"
mongo_client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=True
)

mongo_db = mongo_client['quiz_db']


def check_quiz_set(quiz_set):
    print(quiz_set)