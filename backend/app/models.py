from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserProgress(Base):
    __tablename__ = "user_progress"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    last_set_id = Column(Integer, nullable=False, default=1)


class QuizSetResult(Base):
    __tablename__ = "quiz_set_result"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)  # User ID
    quiz_set_id = Column(String, nullable=False)  # Quiz set id
    quiz_type = Column(String, nullable=False)  # Subject ID
    score = Column(Integer, nullable=False)  # Total score

    # Relationship with QuizResult (one-to-many, quiz_results will be a list of QuizResult objects)
    quiz_results = relationship("QuizResult", backref="quiz_set", cascade="all, delete-orphan")


class QuizResult(Base):
    __tablename__ = "quiz_result"

    id = Column(Integer, primary_key=True, index=True)
    result_id = Column(Integer, ForeignKey("quiz_set_result.id"), nullable=False)  # Foreign key to QuizSetResult
    quiz_id = Column(String, nullable=False)  # Quiz question ID
    user_answer = Column(String, nullable=False)  # User's answer
    is_correct = Column(Integer, nullable=False)  # 1 for correct, 0 for incorrect
