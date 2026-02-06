import asyncio
import json
import os
from openai import OpenAI
import aiohttp
import re

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

async def generate_quiz_from_mongodb(subject, new_quiz_set_number, new_quiz_id):
    """MongoDB에서 기존 퀴즈를 가져와 새로운 퀴즈 생성"""
    existing_quizzes = f"quiz_json/{subject}_offer.json"
    with open(existing_quizzes, "r", encoding="utf-8") as file:
        existing_quizzes = json.load(file)

    new_quiz_set = {
        "quiz_type": f"{subject}",
        "quiz_set_id": f"quiz_set_{new_quiz_set_number}",
        "quiz": []
    }

    async def generate_quiz(quiz, new_quiz_id):
        subject_quiz = quiz["quiz_content"]["subject"]
        topic = quiz["quiz_content"]["topic"]
        sub_topic = quiz["quiz_content"]["sub_topic"]

        with open(f"quiz_json/knowledge_json/{subject.lower()}_knowledge.json", "r", encoding="utf-8") as file2:
            knowledge_json = json.load(file2)

        knowledge_text = knowledge_json.get(sub_topic, "")

        prompt = f"""
        Generate a new question by modifying the given quiz offer.
        knowledge_text: {knowledge_text}
        Quiz offer:
        {{
            "quiz_id": "{subject}_{new_quiz_id}",
            "quiz_content": {{
                "subject": "{subject_quiz}",
                "topic": "{topic}",
                "sub_topic": "<sub_topic>",
                "question_text": "<question_text>",
                "example": null,
                "options": {{
                    "1": "<option_1>",
                    "2": "<option_2>",
                    "3": "<option_3>",
                    "4": "<option_4>"
                }},
                "correct_option": <correct_option>,
                "description": "<description>"
            }},
        }}"""

        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.openai.com/v1/chat/completions", json={
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": "You are a member of the question-setting committee for a written exam that selects outstanding coaches. Generate the quiz based on the provided knowledge_text by Korean. Ensure that the questions prioritize the reliability and validity of the content. Please generate the questions in JSON format, using a formal tone."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "response_format": {'type': 'json_object'}
            }, headers={"Authorization": f"Bearer {client.api_key}"}) as response:
                try:
                    response_data = await response.json()
                    new_quiz = json.loads(response_data["choices"][0]["message"]["content"])
                    new_quiz_set["quiz"].append(new_quiz)
                except KeyError as e:
                    print(f"❌ KeyError 발생: {e}")
                    print("🔍 응답 데이터 전체 출력:")
                    print(json.dumps(response_data, indent=4, ensure_ascii=False))
                    raise

    tasks = []
    for quiz in existing_quizzes["quiz"]:
        task = generate_quiz(quiz, new_quiz_id)
        tasks.append(task)
        new_quiz_id += 1

    await asyncio.gather(*tasks)

    # quiz_id 숫자 부분 기준으로 정렬
    def extract_number(quiz):
        match = re.search(r"(\d+)", quiz["quiz_id"])
        return int(match.group(1)) if match else float('inf')

    new_quiz_set["quiz"].sort(key=extract_number)

    output_path = f"quiz_json/generated_quiz_json/{subject}_{new_quiz_set_number}.json"
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(new_quiz_set, file, ensure_ascii=False, indent=4)

    print(f"새로운 퀴즈셋이 {output_path}에 저장되었습니다! 🎉")

asyncio.run(generate_quiz_from_mongodb(subject="SCT", new_quiz_set_number=10, new_quiz_id=180))
