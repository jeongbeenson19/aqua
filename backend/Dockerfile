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

# FastAPI 애플리케이션 코드 복사
COPY ./app /app

# requirements.txt 파일이 app 폴더에 존재한다고 가정
COPY ./app/requirements.txt /app/requirements.txt

# 필요한 Python 패키지 설치
RUN pip install --no-cache-dir -r /app/requirements.txt

# Nginx 설정 파일 복사
COPY ./nginx.conf /etc/nginx/nginx.conf

# 쉘 스크립트 복사 및 실행 권한 부여
COPY ./start.sh /start.sh
RUN chmod +x /start.sh  # 실행 권한 추가

# FastAPI 및 Nginx 실행
CMD ["/start.sh"]
