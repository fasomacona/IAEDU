from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    anonymous_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    group_name: Mapped[str] = mapped_column(String(100), default="general")
    institution: Mapped[str] = mapped_column(String(100), default="TESCHA")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    submissions = relationship("Submission", back_populates="student")
    hint_requests = relationship("HintRequest", back_populates="student")


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    concepts: Mapped[str] = mapped_column(String(300))  # comma-separated
    difficulty: Mapped[int] = mapped_column(Integer, default=1)
    order_index: Mapped[int] = mapped_column(Integer, default=0)


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"))
    code: Mapped[str] = mapped_column(Text)
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    tests_passed: Mapped[int] = mapped_column(Integer, default=0)
    tests_total: Mapped[int] = mapped_column(Integer, default=0)
    static_errors: Mapped[str] = mapped_column(Text, default="[]")  # JSON string
    execution_time_ms: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="submissions")
    hint_requests = relationship("HintRequest", back_populates="submission")


class HintRequest(Base):
    __tablename__ = "hint_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id"))
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"))
    level: Mapped[int] = mapped_column(Integer)  # 1, 2 or 3
    hint_text: Mapped[str] = mapped_column(Text)
    concept_tags: Mapped[str] = mapped_column(String(300), default="")  # for teacher panel
    filtered: Mapped[bool] = mapped_column(Boolean, default=False)  # True if filter blocked something
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="hint_requests")
    submission = relationship("Submission", back_populates="hint_requests")
