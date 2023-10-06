from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError as sqlalchemyOpError
from typing import Type
from . import Base
from .models import Problem
from .models import Task
from .models import User, Submission, Problem, Task


class DBManager:
    def __init__(self, db_path: str = "data/data.sqlite3"):
        self.engine = create_engine(f"sqlite:///{db_path}")
        print("initind db")
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

    def get_tasks(self) -> list[Task]:
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

    def get_all_problems(self, task_id: int) -> list[Problem]:
        return self.session.query(Problem).filter(Problem.task_id == task_id).all()

    def get_problems(self, task_id: int, user_id: int = 0) -> list[Problem]:
        # take problems where user is not subbmitted or not subbmitted correctly
        """
                define this quey in sqlalchmey
                select *
        from problems
        where task_id = 1 and problem_id not in (
            select problem_id
            from submission
            where user_id = 238864041 and correct
        );
        """
        return (
            self.session.query(Problem)
            .filter(Problem.task_id == task_id)
            .filter(
                ~Problem.problem_id.in_(
                    self.session.query(Submission.problem_id)
                    .filter(Submission.user_id == user_id)
                    .filter(Submission.correct)
                )
            )
            .all()
        )

    def get_submissions(
        self, user_id: int, problem_id: int = -1
    ) -> tuple[list[Submission], list[Submission]]:
        """
        returns two lists of submits, first is correct, second is incorrect

        """
        if problem_id == -1:
            # if task_id is -1, return submissions for all tasks
            return (
                self.session.query(Submission)
                .filter(Submission.user_id == user_id)
                .filter(Submission.correct)
                .all(),
                self.session.query(Submission)
                .filter(Submission.user_id == user_id)
                .filter(~Submission.correct)
                .all(),
            )
        else:
            return (
                self.session.query(Submission)
                .filter(Submission.user_id == user_id)
                .filter(Submission.problem_id == problem_id)
                .filter(Submission.correct)
                .all(),
                self.session.query(Submission)
                .filter(Submission.user_id == user_id)
                .filter(Submission.problem_id == problem_id)
                .filter(~Submission.correct)
                .all(),
            )


db = DBManager()
