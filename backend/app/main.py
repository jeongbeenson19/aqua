import os
import requests
from fastapi import FastAPI, HTTPException, Path, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import urlencode
from dotenv import load_dotenv
from app.crud import get_last_set_id_from_mysql, update_user_progress
from app.database import mongo_db, SessionLocal, engine
from app.models import QuizSetResult, QuizResult, User
from app.schemas import QuizResults
from app.utils import is_collection_exists, validate_quiz_length, validate_quiz_result_length, get_or_create_user, get_db, create_jwt_token, decode_jwt

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")
LOGIN_REDIRECT_URI = "http://localhost:3000/redirection"

# 로그인 요청 URL 생성
@app.get("/auth/kakao/login")
def kakao_login():
    kakao_auth_url = (
        f"https://kauth.kakao.com/oauth/authorize?"
        f"client_id={KAKAO_CLIENT_ID}&"
        f"redirect_uri={KAKAO_REDIRECT_URI}&"
        f"response_type=code"
    )
    return RedirectResponse(kakao_auth_url)


# 카카오 로그인 콜백 처리
@app.get("/auth/kakao/callback")
def kakao_callback(code: str, db: Session = Depends(get_db)):
    # Access Token 요청
    token_url = "https://kauth.kakao.com/oauth/token"
    token_data = {
        "grant_type": "authorization_code",
        "client_id": KAKAO_CLIENT_ID,
        "redirect_uri": KAKAO_REDIRECT_URI,
        "code": code,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    token_response = requests.post(token_url, data=token_data, headers=headers)
    if not token_response.ok:
        raise HTTPException(status_code=400, detail="Failed to get access token")

    token_json = token_response.json()
    access_token = token_json["access_token"]

    # 사용자 정보 요청
    user_info_url = "https://kapi.kakao.com/v2/user/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info_response = requests.get(user_info_url, headers=headers)
    if not user_info_response.ok:
        raise HTTPException(status_code=400, detail="Failed to get user info")

    user_info = user_info_response.json()

    # 사용자 정보 추출 및 회원가입/로그인 처리
    kakao_id = user_info.get("id")
    kakao_account = user_info.get("kakao_account", {})
    email = kakao_account.get("email")
    nickname = kakao_account.get("profile", {}).get("nickname")

    user = get_or_create_user(db, kakao_id=kakao_id, email=email, nickname=nickname)

    # JWT 생성
    jwt_token = create_jwt_token(user_id=user.id)

    query_params = urlencode({
        "jwt_token": jwt_token,
        "user_id": user.user_id,
    })

    redirect_url = f"{LOGIN_REDIRECT_URI}?{query_params}"
    return RedirectResponse(url=redirect_url)
@app.get("/quiz/{quiz_type}/{user_id}")
async def fetch_quiz_set(
    quiz_type: str = Path(
        ...,
        description=(
            "퀴즈의 과목입니다. 허용 가능한 값: [SCT, EDU, PSY, HIS, PHY, KIN, ETH]. "
            "각각 '스포츠사회학', '스포츠교육학', '스포츠심리학', '한국체육사', '운동생리학', '운동역학', '스포츠윤리'를 의미합니다. "
            "예: quiz_type=EDU (스포츠 교육학 퀴즈 요청)"
        )
    ),
    user_id: str = Path(
        ...,
        description=(
            "사용자의 고유 ID. 헤더에서 제공되어야 하며, "
            "필수 입력값입니다. 예: user_id=user_123"
        ),

    ),
    user: User = Depends(decode_jwt)
):
    # 요청 처리 로직
    if user.user_id != user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")

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


@app.post("/quiz/submit/{user_id}")
async def submit_quiz(
    quiz_results: QuizResults,
    user_id: str = Path(..., description="사용자의 고유 ID"),
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

            update_user_progress(session=Session(engine), user_id=user_id, quiz_type=quiz_type)

        return {"quiz_set_id": quiz_set_result.id, "score": quiz_set_result.score}

    except Exception as e:
        print("Error occurred:", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/attempted/{user_id}/list")
async def fetch_attempted_quiz_sets_list(
    user_id: str = Path(..., description="사용자의 고유 ID"),
    user: User = Depends(decode_jwt)
):
    # 요청 처리 로직
    if user.user_id != user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")

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
            # Remove the unwanted fields (quiz_id, subject, topic, sub_topic)
            quiz_content = quiz_data["quiz_content"]
            quiz_content.pop("subject", None)
            quiz_content.pop("topic", None)
            quiz_content.pop("sub_topic", None)

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


@app.get("/my_page/plot/sunburst/{user_id}")
async def my_page_plot(
        user_id: str = Path(..., description="")
):
    """
    마이페이지에 출력한 sunburst 플롯을 요청합니다.
    """
    import pandas as pd
    import plotly.express as px

    with Session(engine) as session_quiz_set_result:
        attempted_quiz_set_result = session_quiz_set_result.query(QuizSetResult).filter(
            QuizSetResult.user_id == user_id
        ).all()

    quiz_set_result_dict = {
        quiz_set.id: {
            "quiz_set_id": quiz_set.quiz_set_id,
            "quiz_type": quiz_set.quiz_type
        }
        for quiz_set in attempted_quiz_set_result
    }

    for result_id, quiz_set_result in quiz_set_result_dict.items():
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

        collection_name = f"{quiz_set_result['quiz_type'].lower()}"

        if not is_collection_exists(mongo_db, collection_name):
            raise Exception(f"Collection '{collection_name}' does not exist.")

            # MongoDB에서 해당 set_id에 해당하는 퀴즈셋 조회
        collection = mongo_db[collection_name]
        quiz_set = collection.find_one({"quiz_set_id": quiz_set_result['quiz_set_id']}, {"_id": 0})

        if not quiz_set:
            raise HTTPException(status_code=404,
                                detail=f"No quiz set found for set_id_{quiz_set_result['quiz_set_id']} in subject '{quiz_set_result['quiz_type']}'.")

        combined_data = {}
        for quiz_id, result in quiz_result_dict.items():
            # MongoDB에서 해당 quiz_id의 데이터를 찾기
            quiz_data = next((quiz for quiz in quiz_set["quiz"] if quiz["quiz_id"] == quiz_id), None)
            if quiz_data:
                # Remove the unwanted fields (quiz_id, subject, topic, sub_topic)
                quiz_content = quiz_data["quiz_content"]
                quiz_content.pop("sub_topic", None)
                quiz_content.pop("question_text", None)
                quiz_content.pop("example", None)
                quiz_content.pop("options", None)
                quiz_content.pop("correct_option", None)
                quiz_content.pop("description", None)

                combined_data[quiz_id] = {
                    "quiz": quiz_data,
                    "is_correct": result["is_correct"]
                }
            else:
                combined_data[quiz_id] = {
                    "quiz": None,  # MongoDB에 퀴즈 데이터가 없을 경우
                    "is_correct": result["is_correct"]
                }

        # JSON 데이터를 DataFrame으로 변환
        rows = []
        for quiz_id, details in combined_data.items():
            row = {
                "quiz_id": quiz_id,
                "subject": details["quiz"]["quiz_content"]["subject"],
                "topic": details["quiz"]["quiz_content"]["topic"],
                "is_correct": "Correct" if details["is_correct"] else "Incorrect"
            }
            rows.append(row)

        df = pd.DataFrame(rows)

        # Sunburst 차트를 그리기 위한 데이터 구조
        fig = px.sunburst(
            df,
            path=["subject", "topic", "is_correct"],  # 계층적 경로
            values=None,  # 비율 기반이 아닌 개수를 사용
            color="is_correct",  # 정답/오답을 색상으로 표현
            color_discrete_map={"Correct": "green", "Incorrect": "red"},
        )

        fig.show()
        plot_json = fig.to_json()

        return {"plot": plot_json}
