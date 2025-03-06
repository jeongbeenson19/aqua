# 베이스 이미지를 Python으로 설정 (FastAPI 서버용)
FROM python:3.10-slim

# Nginx 설치
RUN apt-get update && \
    apt-get install -y nginx && \
    apt-get clean

# 1. Python 3.10 기반 이미지 사용
FROM python:3.10

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 필요한 파일 복사
COPY /app/requirements.txt .

RUN apt-get update && apt-get install -y supervisor


# 4. 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 5. 애플리케이션 코드 복사
COPY . .

# Nginx 설정 파일 복사
COPY ./nginx.conf /etc/nginx/nginx.conf

# 쉘 스크립트 복사 및 실행 권한 부여
COPY ./start.sh /start.sh
RUN chmod +x /start.sh  # 실행 권한 추가


# Supervisord 설정 파일 복사
COPY ./supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Supervisor로 시작
CMD ["/usr/bin/supervisord"]
