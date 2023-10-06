from sqlalchemy import Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import Base


class User(Base):
    __tablename__ = "user"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    deactivated: Mapped[bool] = mapped_column(Boolean)
    is_closed: Mapped[bool] = mapped_column(Boolean)
    can_access_closed: Mapped[bool] = mapped_column(Boolean)
    birth_date: Mapped[str] = mapped_column(String)

    submissions = relationship(
        "Submission",
        back_populates="user",
        uselist=True,
        foreign_keys="Submission.user_id",
    )

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "deactivated": self.deactivated,
            "is_closed": self.is_closed,
            "can_access_closed": self.can_access_closed,
            "birth_date": self.birth_date,
        }


class Submission(Base):
    __tablename__ = "submission"

    submission_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.user_id"))
    problem_id: Mapped[int] = mapped_column(Integer, ForeignKey("problem.problem_id"))
    answer: Mapped[str] = mapped_column(String)
    submission_time: Mapped[str] = mapped_column(String)
    correct: Mapped[bool] = mapped_column(Boolean)

    user = relationship("User", back_populates="submissions")
    problem = relationship("Problem")

    def to_dict(self) -> dict:
        return {
            "submission_id": self.submission_id,
            "user_id": self.user_id,
            "problem_id": self.problem_id,
            "answer": self.answer,
            "correct": self.correct,
            "submission_time": self.submission_time,
        }


class Problem(Base):
    __tablename__ = "problem"

    problem_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("task.task_id"))
    options: Mapped[str] = mapped_column(String)
    correct_option: Mapped[str] = mapped_column(String)
    created_at: Mapped[str] = mapped_column(String)

    submissions = relationship(
        "Submission",
        back_populates="problem",
        uselist=True,
        foreign_keys="Submission.problem_id",
    )
    task = relationship(
        "Task", back_populates="problems", uselist=False, foreign_keys="Problem.task_id"
    )

    def to_dict(self) -> dict:
        return {
            "problem_id": self.problem_id,
            "task_id": self.task_id,
            "options": self.options,
            "correct_option": self.correct_option,
            "created_at": self.created_at,
        }


class Task(Base):

    __tablename__ = "task"

    task_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ege_id: Mapped[int] = mapped_column(Integer)
    subject_id: Mapped[int] = mapped_column(Integer, ForeignKey("subject.subject_id"))
    description: Mapped[str] = mapped_column(String)

    subject = relationship(
        "Subject", back_populates="tasks", uselist=False, foreign_keys="Task.subject_id"
    )
    problems = relationship(
        "Problem",
        back_populates="task",
        uselist=True,
        foreign_keys="Problem.task_id",
    )

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "ege_id": self.ege_id,
            "subject_id": self.subject_id,
            "description": self.description,
        }


class Subject(Base):
    __tablename__ = "subject"

    subject_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)

    tasks = relationship(
        "Task", back_populates="subject", uselist=True, foreign_keys="Task.subject_id"
    )

    def to_dict(self) -> dict:
        return {
            "subject_id": self.subject_id,
            "name": self.name,
            "description": self.description,
        }
