import os
from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
import ssl

# MongoDB 설정
password = quote_plus(os.environ['MONGO_PW'])
MONGO_URI = f"mongodb+srv://jeongbeenson19:{password}@aqua.wchta.mongodb.net/?retryWrites=true&w=majority&appName=aqua"
mongo_client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=True
)

mongo_db = mongo_client['quiz_db']

# 환경 변수에서 RDS 접속 정보를 가져옵니다.
rds_host = os.environ['RDS_HOST']  # 예: mydbinstance.c9akciq32.rds.amazonaws.com
rds_port = os.environ.get('RDS_PORT', '3306')  # 기본 MySQL 포트 3306
my_password = os.environ['MYSQL_PW']
db_name = os.environ['RDS_DB_NAME']  # RDS에서 사용 중인 데이터베이스 이름

# RDS에 연결할 DATABASE_URL 생성
DATABASE_URL = f"mysql+mysqlconnector://admin:{my_password}@{rds_host}:{rds_port}/{db_name}"

# 테스트용 로컬 DATABASE_URL
# DATABASE_URL = f"mysql+mysqlconnector://root:{my_password}@localhost/user_db"

# SQLAlchemy 엔진 및 세션 생성
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
