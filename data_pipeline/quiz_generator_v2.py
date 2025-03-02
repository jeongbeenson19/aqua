import os
import json
import openai
import pymongo
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# ✅ OpenAI API 설정
openai.api_key = os.environ["OPENAI_API_KEY"]

# ✅ MongoDB 설정
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "quiz_db"

mongo_client = pymongo.MongoClient(MONGO_URI)


# ✅ FAISS 설정
FAISS_INDEX_PATH = "faiss_index.idx"
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# ✅ FAISS 인덱스 로드
faiss_index = faiss.read_index(FAISS_INDEX_PATH)

# ✅ FAISS에 저장된 문서 로드 (id -> text 매핑)
with open("faiss_metadata.json", "r", encoding="utf-8") as f:
    faiss_metadata = json.load(f)


def get_similar_knowledge(query_text, top_k=3):
    """FAISS에서 유사한 지식을 검색"""
    query_embedding = embedding_model.encode([query_text])
    distances, indices = faiss_index.search(np.array(query_embedding, dtype=np.float32), top_k)

    related_knowledge = [faiss_metadata[str(idx)] for idx in indices[0] if str(idx) in faiss_metadata]
    return related_knowledge


def generate_quiz_from_mongodb(subject, quiz_set_id, new_quiz_set_number, new_quiz_id: int):
    """MongoDB에서 기존 퀴즈를 가져와 새로운 퀴즈 생성"""
    quiz_collection = mongo_client[DB_NAME][subject]
    existing_quizzes = list(quiz_collection.find({"quiz_set_id": quiz_set_id}).limit(20))  # 기존 퀴즈 20개 로드

    new_quiz_set = {
        "quiz_type": f"{subject}",
        "quiz_set_id": f"quiz_set_{new_quiz_set_number}",
        "quiz": []
    }

    for quiz in existing_quizzes:
        topic = quiz["quiz_content"]["topic"]
        sub_topic = quiz["quiz_content"]["sub_topic"]
        question_text = quiz["quiz_content"]["question_text"]
        example = quiz["quiz_content"]["example"]
        options = quiz["quiz_content"]["options"]
        correct_option = quiz["quiz_content"]["correct_option"]
        description = quiz["quiz_content"]["description"]

        # ✅ FAISS에서 관련 지식 검색
        related_knowledge = get_similar_knowledge(question_text)
        knowledge_text = " ".join(related_knowledge) if related_knowledge else "관련 정보 없음"

        # ✅ OpenAI 프롬프트 생성
        prompt = f"""
        기존의 퀴즈를 변형하여 새로운 문제를 생성하세요. 
        주어진 기존 문제와 관련 정보를 활용하여 새로운 문제를 만들되, 표현과 방식이 달라야 합니다.

        기존 퀴즈:
        - 주제: {topic}
        - 하위 주제: {sub_topic}
        - 문제: {question_text}
        - 예제: {example}
        - 선택지: {options}
        - 정답: {correct_option}
        - 설명: {description}

        관련 지식 (FAISS 참조):
        {knowledge_text}

        새로운 퀴즈를 JSON 형식으로 출력하세요. 형식:
        {{
            "quiz_id": "{subject}_{new_quiz_id}",
            "quiz_content": {{
                "topic": "{topic}",
                "sub_topic": "{sub_topic}",
                "question_text": "새로운 질문",
                "example": 질문에 대한 추가 설명 또는 예시, 필수 아님
                "options": {{
                    "1": "새로운 보기 1",
                    "2": "새로운 보기 2",
                    "3": "새로운 보기 3",
                    "4": "새로운 보기 4"
                }},
                "correct_option": 정답 번호,
                "description": "정답에 대한 설명"
            }}
        }}
        """

        # ✅ ChatGPT 호출
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format="json"
        )

        # ✅ JSON 데이터 변환 후 리스트에 추가
        new_quiz = json.loads(response["choices"][0]["message"]["content"])
        new_quiz_set["quiz"].append(new_quiz)
        new_quiz_id += 1

    # ✅ 새로운 퀴즈셋 JSON 저장
    output_path = f"generated_quiz_json/{subject}_{new_quiz_set_number}.json"
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(new_quiz_set, file, ensure_ascii=False, indent=4)

    print(f"새로운 퀴즈셋이 {output_path}에 저장되었습니다! 🎉")


# ✅ 실행
generate_quiz_from_mongodb(subject="EDU", quiz_set_id=1, new_quiz_set_number=1, new_quiz_id=1)
