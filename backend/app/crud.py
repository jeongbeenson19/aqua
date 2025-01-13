from sqlalchemy.orm import Session
from sqlalchemy import select
from models import UserProgress


def get_last_set_id_from_mysql(user_id: str, subject: str, db_session: Session) -> int:
    query = select(UserProgress.last_set_id).where(
        UserProgress.user_id == user_id, UserProgress.subject == subject
    )
    result = db_session.execute(query).scalar()
    return result if result else 0  # 조회 결과 없으면 기본값 0
