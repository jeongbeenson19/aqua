from sqlalchemy.orm import Session
from sqlalchemy import select, update
from app.models import UserProgress


def get_last_set_id_from_mysql(user_id: str, quiz_type: str, db_session: Session) -> int:
    query = select(UserProgress.last_set_id).where(
        UserProgress.user_id == user_id, UserProgress.quiz_type == quiz_type
    )
    result = db_session.execute(query).scalar()
    print(result)

    # 레코드가 없으면 새로 생성
    if result is None:
        print("Couldn't find the last set id")
        new_progress = UserProgress(user_id=user_id, quiz_type=quiz_type, last_set_id=0)
        db_session.add(new_progress)
        db_session.commit()
        return 0  # 기본값 반환

    return result  # 기존 값 반환


def update_user_progress(session: Session, user_id: str, quiz_type: str):
    stmt = (
        update(UserProgress)
        .where(UserProgress.user_id == user_id, UserProgress.quiz_type == quiz_type)
        .values(last_set_id=UserProgress.last_set_id + 1)  # 기존 값에 +1
    )
    session.execute(stmt)
    session.commit()
