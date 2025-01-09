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
async def fetch_quiz_set(
    subject: str = Query(
        ...,
        description=(
            "퀴즈의 과목입니다. 허용 가능한 값: [SCT, EDU, PSY, HIS, PHY, KIN, ETH]. "
            "각각 '스포츠사회학', '스포츠교육학', '스포츠심리학', '한국체육사', '운동생리학', '운동역학', '스포츠윤리'을 의미합니다. "
            "예: subject=EDU (스포츠 교육학 퀴즈 요청)"
        )
    ),
    user_id: str = Header(
        ...,
        description=(
            "사용자의 고유 ID. 헤더에서 제공되어야 하며, "
            "필수 입력값입니다. 예: user_id=user_123"
        )
)

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
    quiz_set_id = f"quiz_set_{int(set_id) + 1}"
    quiz_set = collection.find_one({"quiz_set_id": quiz_set_id}, {"_id": 0})

    if not quiz_set:
        raise HTTPException(status_code=404, detail=f"No quiz set found for set_id_{quiz_set_id} in subject '{subject}'.")

    return {"subject": subject, "set_id": set_id, "quiz_set": quiz_set}
