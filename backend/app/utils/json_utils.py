import json
from fastapi import HTTPException


def validate_quiz_length(quiz_items):
    # `quiz_items`가 이미 dict라면 바로 사용, 문자열이라면 JSON 파싱
    if isinstance(quiz_items, str):
        try:
            quiz_items = json.loads(quiz_items)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format.")

    # `quiz` 키가 존재하는지 확인
    if "quiz" not in quiz_items:
        raise HTTPException(status_code=400, detail="'quiz' key not found in quiz items.")

    # 길이 확인
    quiz_items_length = len(quiz_items["quiz"])
    if quiz_items_length != 20:
        raise HTTPException(status_code=422, detail=f"Quiz length must be 20, but got {quiz_items_length}")


def validate_quiz_result_length(quiz_items):
    # `quiz_items`가 이미 dict라면 바로 사용, 문자열이라면 JSON 파싱
    if isinstance(quiz_items, str):
        try:
            quiz_items = json.loads(quiz_items)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format.")

    # `quiz_results` 키가 존재하는지 확인
    if "quiz_results" not in quiz_items:
        raise HTTPException(status_code=400, detail="'quiz_results' key not found in quiz items.")

    # 길이 확인
    quiz_items_length = len(quiz_items["quiz_results"])
    if quiz_items_length != 20:
        raise HTTPException(status_code=422, detail=f"Quiz length must be 20, but got {quiz_items_length}")

