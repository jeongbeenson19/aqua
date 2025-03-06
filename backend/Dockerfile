FROM ubuntu:latest
LABEL authors="mac_air"

ENTRYPOINT ["top", "-b"]

# 기본 이미지로 Python을 사용 (FastAPI 서버용)
FROM python:3.10-slim

# Nginx 설치
RUN apt-get update && \
    apt-get install -y nginx && \
    apt-get clean

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# FastAPI 애플리케이션 코드 복사
COPY ./backend /app

# Nginx 설정 파일 복사
COPY ./nginx.conf /etc/nginx/nginx.conf

# Nginx 및 FastAPI 서버 실행
CMD service nginx start && uvicorn main:app --host 0.0.0.0 --port 8000
