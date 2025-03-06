#!/bin/bash

# Nginx 실행 (백그라운드 모드)
nginx

# Nginx가 완전히 실행된 후 FastAPI 서버 실행
sleep 2  # Nginx가 시작되는 시간을 기다립니다
uvicorn app.main:app --host 0.0.0.0 --port 8000
