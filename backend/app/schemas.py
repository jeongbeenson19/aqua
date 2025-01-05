from pydantic import BaseModel
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
