nginx &

# FastAPI 서버 실행
uvicorn app.main:app --host 0.0.0.0 --port 8000