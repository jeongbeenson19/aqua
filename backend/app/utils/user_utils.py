import time
import random
import string
from typing import List, Optional
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
    normalized_email = normalize_profile_field(email)
    normalized_nickname = normalize_profile_field(nickname)

    # 사용자 검색
    user = db.query(User).filter(User.kakao_id == kakao_id).first()
    if not user:
        # 사용자 생성
        user = User(
            kakao_id=kakao_id,
            user_id=generate_custom_id(),
            email=normalized_email,
            nickname=normalized_nickname,
        )
        db.add(user)
        db.commit()
        db.refresh(user)  # 생성된 사용자 객체를 다시 가져오기
        return user

    if apply_user_profile_updates(
        user,
        email=normalized_email,
        nickname=normalized_nickname,
        overwrite_blank_only=True,
    ):
        db.commit()
        db.refresh(user)

    return user


def update_user_info(db: Session, kakao_id: str, email: str, nickname: str):
    """카카오 ID를 기반으로 유저 정보를 업데이트"""
    user = db.query(User).filter(User.kakao_id == kakao_id).first()
    if not user:
        return None  # 유저가 없으면 실패

    apply_user_profile_updates(user, email=email, nickname=nickname)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_user_id(db: Session, user_id: str) -> Optional[User]:
    return db.query(User).filter(User.user_id == user_id).first()


def update_user_profile_by_user_id(db: Session, user_id: str, email: str, nickname: str) -> Optional[User]:
    user = get_user_by_user_id(db, user_id)
    if not user:
        return None

    apply_user_profile_updates(user, email=email, nickname=nickname)
    db.commit()
    db.refresh(user)
    return user


def normalize_profile_field(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None

    normalized_value = value.strip()
    return normalized_value or None


def get_missing_user_profile_fields(user: User) -> List[str]:
    missing_fields = []

    if not normalize_profile_field(user.nickname):
        missing_fields.append("nickname")

    if not normalize_profile_field(user.email):
        missing_fields.append("email")

    return missing_fields


def is_user_profile_incomplete(user: User) -> bool:
    return bool(get_missing_user_profile_fields(user))


def apply_user_profile_updates(
    user: User,
    email: Optional[str],
    nickname: Optional[str],
    overwrite_blank_only: bool = False,
) -> bool:
    normalized_email = normalize_profile_field(email)
    normalized_nickname = normalize_profile_field(nickname)
    was_updated = False

    if overwrite_blank_only:
        if not normalize_profile_field(user.email) and normalized_email:
            user.email = normalized_email
            was_updated = True
        if not normalize_profile_field(user.nickname) and normalized_nickname:
            user.nickname = normalized_nickname
            was_updated = True
        return was_updated

    if user.email != normalized_email:
        user.email = normalized_email
        was_updated = True

    if user.nickname != normalized_nickname:
        user.nickname = normalized_nickname
        was_updated = True

    return was_updated


def generate_custom_id():
    timestamp = int(time.time())  # 현재 시간 (유닉스 타임스탬프)
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{timestamp}-{random_part}"
