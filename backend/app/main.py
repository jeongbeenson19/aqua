import os
import requests
from fastapi import FastAPI, HTTPException, Header, Query, Path
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

DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]


@app.get("/quizzes")
async def fetch_quiz_set(
    quiz_type: str = Query(
        ...,
        description=(
            "퀴즈의 과목입니다. 허용 가능한 값: [SCT, EDU, PSY, HIS, PHY, KIN, ETH]. "
            "각각 '스포츠사회학', '스포츠교육학', '스포츠심리학', '한국체육사', '운동생리학', '운동역학', '스포츠윤리'를 의미합니다. "
            "예: quiz_type=EDU (스포츠 교육학 퀴즈 요청)"
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


@app.get("/attempted/{user_id}/list")
async def fetch_attempted_quiz_sets_list(
    user_id: str = Path(..., description="사용자의 고유 ID")
):
    """
    유저의 풀이 기록을 호출하여 리스트로 반환합니다.
    """
    with Session(engine) as session_quiz_set_result:
        # user_id가 일치하는 데이터를 필터링
        attempted_quiz_sets_list = session_quiz_set_result.query(QuizSetResult).filter(
            QuizSetResult.user_id == user_id).all()

    # 쿼리 결과를 반환
    return {"attempted_quiz_sets": attempted_quiz_sets_list}


@app.get("/attempted/{result_id}/{quiz_type}/{quiz_set_id}")
async def fetch_attempted_quiz_set(
        result_id: int = Path(..., description="/attempted/{user_id}/list의 실행 결과로 반환된 result_id"),
        quiz_type: str = Path(..., description="/attempted/{user_id}/list의 실행 결과로 반환된 quiz_type"),
        quiz_set_id: str = Path(..., description="/attempted/{user_id}/list의 실행 결과로 반환된 quiz_set_id")

):
    """
    /attempted/{user_id}/list의 실행 결과로 반환된 데이터로 오답노트 구성에 필요한 데이터를 요청합니다.
    """
    with Session(engine) as session_quiz_result:
        attempted_quiz_set = session_quiz_result.query(QuizResult).filter(
            QuizResult.result_id == result_id
        ).all()

    quiz_result_dict = {
        quiz.quiz_id: {
            "user_answer": quiz.user_answer,
            "is_correct": quiz.is_correct
        }
        for quiz in attempted_quiz_set
    }

    collection_name = f"{quiz_type.lower()}"

    if not is_collection_exists(mongo_db, collection_name):
        raise Exception(f"Collection '{collection_name}' does not exist.")

        # MongoDB에서 해당 set_id에 해당하는 퀴즈셋 조회
    collection = mongo_db[collection_name]
    quiz_set = collection.find_one({"quiz_set_id": quiz_set_id}, {"_id": 0})

    if not quiz_set:
        raise HTTPException(status_code=404,
                            detail=f"No quiz set found for set_id_{quiz_set_id} in subject '{quiz_type}'.")

    combined_data = {}
    for quiz_id, result in quiz_result_dict.items():
        # MongoDB에서 해당 quiz_id의 데이터를 찾기
        quiz_data = next((quiz for quiz in quiz_set["quiz"] if quiz["quiz_id"] == quiz_id), None)
        if quiz_data:
            combined_data[quiz_id] = {
                "quiz": quiz_data,
                "user_answer": int(result["user_answer"]),
                "is_correct": result["is_correct"]
            }
        else:
            combined_data[quiz_id] = {
                "quiz": None,  # MongoDB에 퀴즈 데이터가 없을 경우
                "user_answer": int(result["user_answer"]),
                "is_correct": result["is_correct"]
            }

    return combined_data


@app.post("/report/{quiz_type}/{quiz_set_id}/{quiz_id}")
async def create_quiz_report(
        title: str,
        description: str,
        quiz_type: str = Path(..., description=""),
        quiz_set_id: str = Path(..., description=""),
        quiz_id: str = Path(..., description=""),

):
    """
    유저가 발견한 오류를 디스코드 웹 훅으로 전송합니다.
    """
    embed = {
        "title": title,
        "description": description,
        "color": 3447003,  # 블루 컬러
        "fields": [
            {"name": "Quiz Type", "value": quiz_type, "inline": True},
            {"name": "Quiz Set ID", "value": quiz_set_id, "inline": True},
            {"name": "Quiz ID", "value": quiz_id, "inline": True},
        ],
    }

    # 디스코드 웹훅 요청 데이터
    payload = {
        "content": "**새로운 오류 제보가 접수되었습니다!**",
        "embeds": [embed]
    }

    # 웹훅 전송
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if response.status_code != 204:  # 204 No Content는 성공 응답
        raise HTTPException(status_code=response.status_code, detail="Failed to send webhook")

    return {"message": "Bug report sent to Discord successfully"}
