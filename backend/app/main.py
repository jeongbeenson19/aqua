from fastapi import FastAPI, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from crud import get_last_set_id_from_mysql
from database import mongo_db, SessionLocal, engine
from models import QuizSetResult, QuizResult
from schemas import QuizResults
from utils import is_collection_exists, validate_quiz_length, validate_quiz_result_length

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
    quiz_type: str = Query(
        ...,
        description=(
            "퀴즈의 과목입니다. 허용 가능한 값: [SCT, EDU, PSY, HIS, PHY, KIN, ETH]. "
            "각각 '스포츠사회학', '스포츠교육학', '스포츠심리학', '한국체육사', '운동생리학', '운동역학', '스포츠윤리'를 의미합니다. "
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
    collection_name = f"{quiz_type.lower()}"

    # 해당 컬렉션 존재 여부 확인
    if not is_collection_exists(mongo_db, collection_name):
        raise Exception(f"Collection '{collection_name}' does not exist.")

    # MySQL에서 last_set_id 조회
    if user_id:
        with SessionLocal() as db_session:
            set_id = get_last_set_id_from_mysql(user_id, quiz_type, db_session)

    # MongoDB에서 해당 set_id에 해당하는 퀴즈셋 조회
    collection = mongo_db[collection_name]
    quiz_set_id = f"quiz_set_{int(set_id) + 1}"
    quiz_set = collection.find_one({"quiz_set_id": quiz_set_id}, {"_id": 0})

    if not quiz_set:
        raise HTTPException(status_code=404, detail=f"No quiz set found for set_id_{quiz_set_id} in subject '{quiz_type}'.")

    validate_quiz_length(quiz_set)

    return {"quiz_type": quiz_type, "set_id": set_id, "quiz_set": quiz_set}


@app.post("/submit-quiz")
async def submit_quiz(
    quiz_results: QuizResults,
    user_id: str = Header(..., description="사용자의 고유 ID")
):
    """
    퀴즈 결과를 제출하고 점수를 저장합니다.
    """
    try:
        validate_quiz_result_length(quiz_results.dict())
        quiz_set_id = quiz_results.quiz_set_id
        quiz_type = quiz_results.quiz_type
        score = quiz_results.score

        with Session(engine) as session_quiz_set_result:
            # QuizSetResult 생성
            quiz_set_result = QuizSetResult(
                user_id=user_id,
                quiz_set_id=quiz_set_id,
                quiz_type=quiz_type,
                score=score,
            )
            session_quiz_set_result.add(quiz_set_result)
            session_quiz_set_result.commit()
            session_quiz_set_result.refresh(quiz_set_result)
            result_id = quiz_set_result.id
            print("QuizSetResult created with ID:", result_id)

            with Session(engine) as session_quiz_result:
                # QuizResult 저장
                for result in quiz_results.quiz_results:
                    print("Processing quiz result:", result)
                    quiz_result = QuizResult(
                        result_id=result_id,
                        quiz_id=result.quiz_id,
                        user_answer=result.user_answer,
                        is_correct=result.is_correct
                    )
                    session_quiz_result.add(quiz_result)

                session_quiz_result.commit()
                print("All quiz results committed successfully.")

        return {"quiz_set_id": quiz_set_result.id, "score": quiz_set_result.score}

    except Exception as e:
        print("Error occurred:", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
