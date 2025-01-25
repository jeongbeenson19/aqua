import jwt
from datetime import datetime, timedelta
from fastapi import Security, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.database import SessionLocal
from app.models import User
from .user_utils import get_db


SECRET_KEY = "your_secret_key"  # 토큰 서명용 비밀키
ALGORITHM = "HS256"            # 해싱 알고리즘

security = HTTPBearer()


def create_jwt_token(user_id: str):
    """
    JWT 토큰을 생성합니다.
    """
    expiration = datetime.utcnow() + timedelta(hours=24)  # 만료 시간 설정
    payload = {
        "sub": str(user_id),
        "exp": expiration,  # 만료 시간
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_jwt(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: SessionLocal = Depends(get_db),
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid JWT payload")

        # 사용자 확인
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="JWT has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid JWT token")