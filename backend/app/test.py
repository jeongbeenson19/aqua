from fastapi.testclient import TestClient

# FastAPI 앱 임포트
from main import app

client = TestClient(app)


def test_with_headers():
    response = client.get(
        "/quizzes",
        params={"subject": "edu"},
        headers={"User-ID": "user_123"}  # 테스트용 헤더 추가
    )
    print(response.status_code)
    print(response.json())


# 테스트 실행
if __name__ == "__main__":
    test_with_headers()
