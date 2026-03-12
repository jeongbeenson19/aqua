import re
from pydantic import BaseModel, ValidationError, model_validator, conint, field_validator
from typing import List, Dict, Optional


EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


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


class UserProfileResponse(BaseModel):
    user_id: str
    nickname: Optional[str]
    email: Optional[str]
    missing_fields: List[str]
    profile_required: bool


class UserProfileUpdate(BaseModel):
    nickname: str
    email: str

    @field_validator("nickname", "email", mode="before")
    @classmethod
    def strip_text_fields(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("nickname")
    @classmethod
    def validate_nickname(cls, value: str):
        if not value:
            raise ValueError("nickname must not be empty")
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str):
        if not value:
            raise ValueError("email must not be empty")
        if not EMAIL_PATTERN.fullmatch(value):
            raise ValueError("email format is invalid")
        return value
