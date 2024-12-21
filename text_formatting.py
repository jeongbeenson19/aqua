import os
import json
from openai import OpenAI

# OpenAI API Key 설정
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# OCR에서 추출된 텍스트 로드
with open('quiz_texts/2022A_2.txt', 'r', encoding='utf-8') as file:
    data = file.read()
    # OpenAI GPT-4 요청용 프롬프트 작성
    prompt = f"""
Given the following plain text from an OCR extraction, please structure each question into the following JSON format:

{{
    "subject": "<subject_name>",  # Select one subject from the following: 스포츠사회학, 스포츠교육학, 스포츠심리학, 한국체육사, 운동생리학, 운동역학, 스포츠윤리
    "topic": "<topic_name>",  # Extract topic based on the question context
    "sub_topic": "<sub_topic_name>",  # Generate sub_topic based on the question content or field of study
    "question_text": "<question_text>",  # Extract the full question text
    "example": [
        "<example_text>" 
    ],  # Extract example if <보기> or further description exists in question, otherwise set options as Null
    # if it has multiple sentence, divide by line break
    "options": {{
        "1": "<option1>",
        "2": "<option2>",
        "3": "<option3>",
        "4": "<option4>"
    }},
    "correct_option": <correct_option_number>,  # Generate the correct option number based on the question
    "description": "<description>"  # Fill this field with a description or additional information related to the question by Korean
}}

The text is as follows:
{data}

- Extract each question from the text, including the subject, topic, and all relevant details.
- example and options could include Korean symbol(㉠, ㉡, ㉢, ㉣, ㉤, ㉥). if it extracted as number or other symbol, change to Korean symbol
- Generate and fill the text for `sub_topic`, `correct_option`, and `description` fields based on the context of each question.
- Ensure that the extracted data is valid JSON and structured according to the specified format.
- If the text file contains multiple questions, output them as a JSON array.
"""

# OpenAI API 호출
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant that extracts and structures quiz questions."
                                      "and Filled the empty space with your knowledge about the sports science except option"},
        {"role": "user", "content": prompt}
    ],
    response_format={"type": "json_object"}
)

# 결과를 JSON으로 변환
quiz_data = json.loads(response.choices[0].message.content)


# 결과 저장
with open('quiz_json/quiz_output2.json', 'w', encoding='utf-8') as json_file:
    json.dump(quiz_data, json_file, ensure_ascii=False, indent=4)

print("Quiz data successfully extracted and saved to 'quiz_json/quiz_output.json'")
