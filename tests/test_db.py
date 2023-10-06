import os
from db.db import DBManager
from db import models
import pytest


@pytest.fixture
def db_instance():
    db = DBManager("test_db.sqlite3")
    # add some test data such as tasks and problems
    for i in range(1, 4):
        db.add_task(
            models.Task(
                ege_id=i + 5,
                subject_id=i,
                description=f"Test task {i}",
            )
        )
        for _ in range(1, 6):
            db.add_problem(
                models.Problem(
                    task_id=i,
                    options=",".join([f"Option {k}" for k in range(1, 5)]),
                    correct_option=1,
                    created_at="2021-01-01",
                )
            )

    yield db
    os.remove("test_db.sqlite3")


def test_tasks(db_instance):

    tasks = db_instance.get_tasks()
    assert len(tasks) == 3


def test_problems(db_instance: DBManager):
    problems = db_instance.get_problems(1)
    assert len(problems) == 5


def test_submitions(db_instance: DBManager):
    db_instance.add_submission(
        models.Submission(
            user_id=1,
            problem_id=1,
            answer=1,
            correct=True,
            submission_time="2021-01-01",
        )
    )
    db_instance.add_submission(
        models.Submission(
            user_id=1,
            problem_id=2,
            answer=2,
            correct=False,
            submission_time="2021-01-01",
        )
    )
    db_instance.add_submission(
        models.Submission(
            user_id=1,
            problem_id=9,
            correct=True,
            answer=1,
            submission_time="2021-01-01",
        )
    )

    # we added 5 problems for each task
    # and 2 correct submission for 1 task
    # so we should have 4 problems for 1 task
    print(len(db_instance.get_problems(1, 1)))
    assert len(db_instance.get_problems(1, 1)) == 4
    assert len(db_instance.get_problems(1)) == 5


def test_all_stats(db_instance: DBManager):
    db_instance.add_submission(
        models.Submission(
            user_id=1,
            problem_id=1,
            answer=1,
            correct=True,
            submission_time="2021-01-01",
        )
    )
    db_instance.add_submission(
        models.Submission(
            user_id=1,
            problem_id=2,
            answer=2,
            correct=False,
            submission_time="2021-01-01",
        )
    )
    db_instance.add_submission(
        models.Submission(
            user_id=1,
            problem_id=9,
            correct=True,
            answer=1,
            submission_time="2021-01-01",
        )
    )

    correct, incorrect = db_instance.get_submissions(1)
    assert len(correct) == 2
    assert len(incorrect) == 1


def test_one_task_stats(db_instance: DBManager):
    db_instance.add_submission(
        models.Submission(
            user_id=1,
            problem_id=1,
            answer=1,
            correct=True,
            submission_time="2021-01-01",
        )
    )
    db_instance.add_submission(
        models.Submission(
            user_id=1,
            problem_id=1,
            answer=2,
            correct=False,
            submission_time="2021-01-01",
        )
    )
    db_instance.add_submission(
        models.Submission(
            user_id=1,
            problem_id=1,
            correct=False,
            answer=2,
            submission_time="2021-01-01",
        )
    )

    correct, incorrect = db_instance.get_submissions(1, 1)
    assert len(correct) == 1
    assert len(incorrect) == 2


def test_one_task_stats_not_found(db_instance: DBManager):
    correct, incorrect = db_instance.get_submissions(1, 1)
    assert len(correct) == 0
    assert len(incorrect) == 0


def test_many_stats(db_instance: DBManager):
    # creating 6 submissions for 3 tasks (2 for each)
    # 1 correct and 1 incorrect
    # get_all stats should return 3 correct and 3 incorrect
    for i in range(1, 4):
        db_instance.add_submission(
            models.Submission(
                user_id=1,
                problem_id=i,
                answer=1,
                correct=True,
                submission_time="2021-01-01",
            )
        )
        db_instance.add_submission(
            models.Submission(
                user_id=1,
                problem_id=i,
                answer=2,
                correct=False,
                submission_time="2021-01-01",
            )
        )
    for i in range(1, 4):
        assert len(db_instance.get_submissions(1, i)[0]) == 1
        assert len(db_instance.get_submissions(1, i)[1]) == 1


def test_problems_not_found(db_instance: DBManager):
    problems = db_instance.get_problems(100)
    assert len(problems) == 0
