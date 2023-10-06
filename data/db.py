from typing import List
from typing import List
from typing import Type
from typing import Type

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError as sqlalchemyOpError
from typing import Type
from . import Base
from .models import Problem
from .models import Task
from .models import User, Submission, Problem, Task


class DBManager:
    def __init__(self, db_path: str = "data.sqlite3"):
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    # create add, update methods for each model
    def add_user(self, user: User):
        # check if user exists update, otherwise add
        if self.session.query(User).filter_by(user_id=user.user_id).first():
            self.update_user(user)
        else:
            self.session.add(user)
            self.session.commit()

    def add_submission(self, submission: Submission):
        self.session.add(submission)
        self.session.commit()

    def add_problem(self, problem: Problem):
        self.session.add(problem)
        self.session.commit()

    def add_task(self, task: Task):
        self.session.add(task)
        self.session.commit()

    def get_tasks(self) -> list[Type[Task]]:
        return self.session.query(Task).all()

    def update_user(self, user: User):
        self.session.merge(user)
        self.session.commit()

    def update_task(self, task: Task):
        self.session.merge(task)
        self.session.commit()

    def update_problem(self, problem: Problem):
        self.session.merge(problem)
        self.session.commit()

    def get_problems(self, task_id: int) -> list[Type[Problem]]:
        return self.session.query(Problem).where(Problem.task_id == task_id).all()


db = DBManager()
