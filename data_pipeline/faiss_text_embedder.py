import os
import openai
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# OpenAI API 키 설정
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

# 원본 및 저장 디렉토리 설정
BASE_DIR = "quiz_texts/2025_psy_summary"  # 원본 텍스트 파일이 위치한 디렉토리
OUTPUT_DIR = "quiz_texts/2025_psy_summary/preprocessed"  # 수정된 텍스트 저장 디렉토리
os.makedirs(OUTPUT_DIR, exist_ok=True)  # 디렉토리가 없으면 생성

# FAISS index 생성
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
dimension = embedding_model.get_sentence_embedding_dimension()
index = faiss.IndexFlatL2(dimension)


def list_text_files(base_dir):
    """지정된 디렉토리에서 모든 .txt 파일을 검색하여 경로 리스트 반환"""
    text_files = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".txt"):
                text_files.append(os.path.join(root, file))
    return text_files


def read_file(file_path):
    """텍스트 파일의 내용을 읽어 반환"""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def refine_text_with_chatgpt(text):
    client = openai.OpenAI()  # 새로운 클라이언트 객체 생성

    response = client.chat.completions.create(  # 최신 방식
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "다음 텍스트를 자연스럽게 수정해주세요."},
            {"role": "user", "content": text}
        ]
    )

    return response.choices[0].message.content  # 최신 API 방식


def text_to_embedding(text):
    """텍스트를 임베딩 벡터로 변환"""
    return embedding_model.encode([text])[0]


def save_processed_text(file_path, refined_text):
    """수정된 텍스트를 OUTPUT_DIR에 저장"""
    file_name = os.path.basename(file_path)
    output_path = os.path.join(OUTPUT_DIR, file_name)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(refined_text)
    return output_path


def process_and_store():
    """텍스트 파일을 읽고 정제하여 FAISS에 저장 및 수정된 파일 저장"""
    text_files = list_text_files(BASE_DIR)
    for file in text_files:
        raw_text = read_file(file)
        refined_text = refine_text_with_chatgpt(raw_text)  # ChatGPT API로 수정
        # embedding = text_to_embedding(refined_text)  # 임베딩 변환
        #
        # index.add(np.array([embedding], dtype=np.float32))  # FAISS 저장
        saved_file_path = save_processed_text(file, refined_text)  # 수정된 텍스트 저장
        print(f"Processed and saved: {saved_file_path}")

    # # FAISS 인덱스 저장
    # faiss.write_index(index, "faiss_index.bin")
    # print("FAISS index saved as faiss_index.bin")


if __name__ == "__main__":
    process_and_store()
