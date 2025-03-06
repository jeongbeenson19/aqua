#!/bin/bash

# Nginx 서버 시작
service nginx start

# FastAPI 서버 시작 (예: uvicorn)
uvicorn app.main:app --host 0.0.0.0 --port 8000
