from fastapi import FastAPI, HTTPException, Header, Query, Depends
from sqlalchemy.orm import Session
from database import mongo_db, SessionLocal
from crud import get_last_set_id_from_mysql
from schemas import QuizSet, QuizResults
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


@app.post("/submit-quiz")
async def submit_quiz(
    user_id: str = Header(
        ...,
        description=(
            "사용자의 고유 ID. 헤더에서 제공되어야 하며, "
            "필수 입력값입니다. 예: user_id=user_123"
        )
    ),
    quiz_results: QuizResults = Depends()
):
    """
    퀴즈 결과를 제출하고 점수를 계산하여 저장합니다.
    """
    from database import SessionLocal
    from models import QuizSetResult, QuizResult

    quiz_set_id = quiz_results.quiz_set_id
    quiz_type = quiz_results.quiz_type
    score = quiz_results.score

    # QuizSetResult 생성
    with SessionLocal() as db:
        # QuizSetResult 생성
        quiz_set_result = QuizSetResult(
            user_id=user_id,
            quiz_set_id=quiz_set_id,
            quiz_type=quiz_type,
            score=score,
        )
        db.add(quiz_set_result)
        db.commit()

        db.refresh(quiz_set_result)

        # QuizResult 저장
        for result in quiz_results.quiz_results:
            quiz_result = QuizResult(
                result_id=quiz_set_result.id,  # 참조할 result_id를 quiz_set_result.id로 설정
                quiz_id=result.quiz_id,  # Quiz question ID
                user_answer=result.user_answer,  # User's answer
                is_correct=result.is_correct  # Correct or incorrect answer
            )
            db.add(quiz_result)

        db.commit()

    return {"quiz_set_id": quiz_set_result.id, "score": quiz_set_result.score}