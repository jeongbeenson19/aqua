import time
import random
import string
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User


# DB 세션 유틸리티
def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()  # ✅ 트랜잭션이 자동으로 `COMMIT`되도록 보장
    except:
        db.rollback()
        raise
    finally:
        db.close()


# 사용자 검색 또는 생성 함수
def get_or_create_user(db: Session, kakao_id: str, email: str, nickname: str):

    # 사용자 검색
    user = db.query(User).filter(User.kakao_id == kakao_id).first()
    if not user:
        # 사용자 생성
        user = User(kakao_id=kakao_id, user_id=generate_custom_id(), email=email, nickname=nickname)
        db.add(user)
        db.commit()
        db.refresh(user)  # 생성된 사용자 객체를 다시 가져오기

    return user


def update_user_info(db: Session, kakao_id: str, email: str, nickname: str):
    """카카오 ID를 기반으로 유저 정보를 업데이트"""
    user = db.query(User).filter(User.kakao_id == kakao_id).first()
    if not user:
        return None  # 유저가 없으면 실패

    user.email = email
    user.nickname = nickname
    db.commit()
    db.refresh(user)
    return user


def generate_custom_id():
    timestamp = int(time.time())  # 현재 시간 (유닉스 타임스탬프)
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{timestamp}-{random_part}"
