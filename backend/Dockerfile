FROM ubuntu:latest
LABEL authors="mac_air"

ENTRYPOINT ["top", "-b"]

# 1. Python 3.10 기반 이미지 사용
FROM python:3.10

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 필요한 파일 복사
COPY /app/requirements.txt .

# 4. 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 5. 애플리케이션 코드 복사
COPY . .

# 6. FastAPI 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
