from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import UserProgress


def get_last_set_id_from_mysql(user_id: str, quiz_type: str, db_session: Session) -> int:
    query = select(UserProgress.last_set_id).where(
        UserProgress.user_id == user_id, UserProgress.quiz_type == quiz_type
    )
    result = db_session.execute(query).scalar()
    return result if result else 0  # 조회 결과 없으면 기본값 0
