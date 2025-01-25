from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    kakao_id = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(String(50), unique=True, index=True, nullable=False)  # External unique user ID
    email = Column(String(255), nullable=True)
    nickname = Column(String(100), nullable=True)

    # Relationship to other tables
    progress = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    quiz_set_results = relationship("QuizSetResult", back_populates="user", cascade="all, delete-orphan")


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False)
    quiz_type = Column(String(255), nullable=False)
    last_set_id = Column(Integer, nullable=False, server_default="1")  # Set default value at the DB level

    # Relationship to User
    user = relationship("User", back_populates="progress")


class QuizSetResult(Base):
    __tablename__ = "quiz_set_result"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False)
    quiz_set_id = Column(String(255), nullable=False)  # Quiz set ID
    quiz_type = Column(String(255), nullable=False)  # Subject ID
    score = Column(Integer, nullable=False)  # Total score

    # Relationship with QuizResult
    quiz_results = relationship("QuizResult", back_populates="quiz_set", cascade="all, delete-orphan")
    user = relationship("User", back_populates="quiz_set_results")


class QuizResult(Base):
    __tablename__ = "quiz_result"

    id = Column(Integer, primary_key=True, index=True)
    result_id = Column(Integer, ForeignKey("quiz_set_result.id"), nullable=False)  # Foreign key to QuizSetResult
    quiz_id = Column(String(255), nullable=False)  # Quiz question ID
    user_answer = Column(String(255), nullable=False)  # User's answer
    is_correct = Column(Boolean, nullable=False)  # Use Boolean instead of Integer

    # Relationship to QuizSetResult
    quiz_set = relationship("QuizSetResult", back_populates="quiz_results")
