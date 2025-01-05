from fastapi import FastAPI, HTTPException, Header, Query
from sqlalchemy.orm import Session
from database import mongo_db, SessionLocal
from crud import get_last_set_id_from_mysql
from schemas import QuizSet
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/quizzes")
async def get_subject_quizzes(
    subject: str = Query(..., description="The subject of the quiz, e.g., 'math' or 'science'"),
    user_id: str = Header(None, description="User ID for personalized quiz progress")
):
    # MongoDB 컬렉션 이름 생성
    collection_name = f"{subject.lower()}"

    # 해당 컬렉션 존재 여부 확인
    if collection_name not in mongo_db.list_collection_names():
        raise HTTPException(status_code=404, detail=f"Subject '{subject}' not found.")

    # MySQL에서 last_set_id 조회
    set_id = 0  # 기본값
    if user_id:
        with SessionLocal() as db_session:
            set_id = get_last_set_id_from_mysql(user_id, subject, db_session)

    # MongoDB에서 해당 set_id에 해당하는 퀴즈셋 조회
    collection = mongo_db[collection_name]
    quiz_set_id = f"quiz_set_{set_id}"
    quiz_set = collection.find_one({"quiz_set_id": quiz_set_id}, {"_id": 0})

    if not quiz_set:
        raise HTTPException(status_code=404, detail=f"No quiz set found for set_id_{quiz_set_id} in subject '{subject}'.")

    return {"subject": subject, "set_id": set_id, "quiz_set": quiz_set}
