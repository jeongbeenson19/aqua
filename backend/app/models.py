from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserProgress(Base):
    __tablename__ = "user_progress"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    last_set_id = Column(Integer, nullable=False, default=1)
