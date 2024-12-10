import os
import json
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Dict
import pandas as pd

API_KEY = os.environ.get("OPENAI_API_KEY")


# 모델 정의
class Question(BaseModel):
    subject: str
    topic: str
    sub_topic: str = Field(alias="sub_topic")
    question_text: str
    options: List[str]
    choices: Dict[str, str]
    correct_option: int
    description: str
    created_at: str


# GCP Vision API에서 추출된 텍스트를 사용
data = open("quiz_texts/2022A_0.txt")
data = data.read()

client = OpenAI(api_key=API_KEY, timeout=60)

# 프롬프트 작성
prompt = f"""
Given the following plain text from an OCR extraction, please structure each question into the following format:
{{
    "subject": "<subject_name>",
    "topic": "<topic_name>",
    "sub_topic": "<sub_topic_name>",
    "question_text": "<question_text>",
    "options": ["<option1>", "<option2>", "<option3>", "<option4>"],
    "choices": {{
        "1": "<option1, option2>",
        "2": "<option1, option3>",
        "3": "<option2, option4>",
        "4": "<option1, option3, option4>"
    }},
    "correct_option": <correct_option_number>,
    "description": "<description>"
}}
The text is as follows:
{data}

Extract each question in the text, including the subject, topic, and all relevant details, and provide it in the above structure. Be sure to capture the question options and the correct answer based on the format in the text.
"""

# OpenAI API를 사용하여 문제 구조화
completion = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant that extracts and structures quiz questions."},
        {"role": "user", "content": prompt}
    ],
    response_format=Question,
)

# 구조화된 문제 출력
quiz_data = completion.choices[0].message.parsed
print(quiz_data)
with open('quiz_json/quiz_output.json', 'w', encoding='utf-8') as json_file:
    json.dump(quiz_data, json_file, ensure_ascii=False, indent=4)


