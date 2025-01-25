from pydantic import BaseModel, ValidationError, model_validator, conint
from typing import List, Dict


class QuizContent(BaseModel):
    subject: str
    topic: str
    sub_topic: str
    question_text: str
    example: List[str] = []  # 기본값을 빈 리스트로 설정
    options: Dict[str, str]
    correct_option: int
    description: str


class Quiz(BaseModel):
    quiz_id: str
    quiz_content: QuizContent


class QuizSet(BaseModel):
    quiz_type: str
    quiz_set_id: str
    quiz: List[Quiz]


class QuizResultItem(BaseModel):
    quiz_id: str
    user_answer: str
    is_correct: conint(ge=0, le=1)

    @model_validator(mode="before")  # 모드가 "before"일 경우, 모델을 생성하기 전에 유효성 검사
    def validate_is_correct(cls, values):
        is_correct = values.get('is_correct')
        if is_correct not in (0, 1):
            raise ValueError("is_correct must be either 0 (incorrect) or 1 (correct)")
        return values


class QuizResults(BaseModel):
    quiz_set_id: str
    quiz_type: str
    score: int
    quiz_results: List[QuizResultItem]
