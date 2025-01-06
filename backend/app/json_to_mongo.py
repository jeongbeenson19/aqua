import json
from pymongo import MongoClient
from urllib.parse import quote_plus


# MongoDB 연결 설정
def connect_to_mongodb(uri="mongodb://localhost:27017/", db_name="quiz_db"):
    client = MongoClient(uri)
    db = client[db_name]
    return db


def connect_to_mongodb_atlas(db_name="quiz_db"):
    password = quote_plus("9bZYDLX@UWs2yF7")
    uri = f"mongodb+srv://jeongbeenson19:{password}@aqua.wchta.mongodb.net/?retryWrites=true&w=majority&appName=aqua"
    client = MongoClient(uri)
    db = client[db_name]
    return db


# JSON 파일을 읽고 MongoDB에 업로드
def upload_quiz_set_to_mongodb(file_path, db):
    collection_name = file_path.split("/")[-1].split("_")[0]
    print(collection_name)
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

        # 'quiz_sets' 컬렉션에 데이터 업로드
        collection = db[f"{collection_name.lower()}"]
        collection.insert_one(data)
        print(f"Data from {file_path} has been uploaded to MongoDB.")


if __name__ == "__main__":
    # MongoDB 연결
    db = connect_to_mongodb_atlas()

    # JSON 파일 경로 (사용자 파일 경로 지정)
    file_path = "../../data_pipeline/quiz_json/EDU_quiz_set_1.json"

    # 업로드 실행
    upload_quiz_set_to_mongodb(file_path, db)
