# AQUA

AQUA is a full-stack quiz platform for sports instructor certification prep. It combines a React frontend, a FastAPI backend, and a data pipeline that turns source materials into quiz sets.

## What This Repo Contains

- `frontend/`: React app for quiz taking, review, and personal analytics.
- `backend/`: FastAPI API server, Kakao login, JWT auth, MySQL for user/progress, MongoDB for quiz content.
- `data_pipeline/`: OCR, parsing, quiz generation, and upload scripts.

## Architecture (High Level)

- Frontend calls the backend API for login, quiz sets, submissions, and review data.
- Backend stores quiz sets in MongoDB and user/progress data in MySQL.
- Data pipeline generates quiz content and uploads it to MongoDB.

## Quick Start (Local)

### Backend

1. `cd backend`
2. `python -m venv .venv`
3. `source .venv/bin/activate`
4. `pip install -r app/requirements.txt`
5. Create `backend/.env` using the variables in the Env Vars section.
6. `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

### Frontend

1. `cd frontend`
2. `npm install`
3. Create `frontend/.env` with `REACT_APP_BACKEND_URL=http://localhost:8000`
4. `npm start`

### Docker (Backend + MySQL + Nginx)

1. `cd backend`
2. Ensure `backend/.env` is set.
3. `docker compose up --build`

## Env Vars

### Backend (`backend/.env`)

- `DATABASE_PY_URL`: SQLAlchemy DB URL for MySQL.
- `MONGO_URI`: Full MongoDB Atlas URI (recommended).
- `MONGO_USER`: Optional if you do not set `MONGO_URI`.
- `MONGO_PW`: Optional if you do not set `MONGO_URI`.
- `MONGO_HOST`: Optional if you do not set `MONGO_URI` (for example `cluster0.xxxxx.mongodb.net`).
- `SECRET_KEY`: JWT signing secret.
- `ALGORITHM`: JWT algorithm, for example `HS256`.
- `KAKAO_CLIENT_ID`: Kakao OAuth client ID.
- `KAKAO_REDIRECT_URI`: Kakao OAuth redirect URI.
- `LOGIN_REDIRECT_URI`: Frontend redirect URI after login.
- `DISCORD_WEBHOOK_URL`: Webhook for user bug reports.
- `DOMAIN`: App domain (used by backend).
- `RDS_HOST`: Optional if you build DB URL yourself.
- `RDS_PORT`: Optional if you build DB URL yourself.
- `RDS_DB_NAME`: Optional if you build DB URL yourself.
- `MYSQL_PW`: Optional if you build DB URL yourself.

### Frontend (`frontend/.env`)

- `REACT_APP_BACKEND_URL`: Backend base URL.

### Data Pipeline (shell env)

- `OPENAI_API_KEY`: Used by quiz generation and parsing scripts.
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to the Google Vision service account JSON.
- `MONGO_PW`: Used by the uploader script.

## Data Pipeline Overview

1. OCR PDFs into text using `data_pipeline/data_extractor.py`.
2. Parse OCR text into structured JSON using `data_pipeline/data_parser.py`.
3. Generate new quiz sets using `data_pipeline/quiz_generator.py` or `data_pipeline/quiz_generator_v4.py`.
4. Upload quiz sets to MongoDB using `data_pipeline/quiz_uploader.py`.

## Key Files

- `backend/app/main.py`: FastAPI routes and core logic.
- `backend/app/database.py`: MongoDB + MySQL configuration.
- `backend/app/utils/token_utils.py`: JWT utilities.
- `frontend/src/pages/quiz.js`: Quiz UI and flow.
- `data_pipeline/data_extractor.py`: PDF to OCR text.
- `data_pipeline/data_parser.py`: OCR text to JSON via OpenAI.
- `data_pipeline/quiz_uploader.py`: Upload quiz sets to MongoDB.

## Notes

- Do not commit `.env` files or credential JSON files.
- The pipeline scripts are intended to be run manually and may require you to edit input paths inside the scripts.
