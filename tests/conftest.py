import copy
from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(autouse=True)
def reset_in_memory_state() -> Iterator[None]:
    initial_activities = copy.deepcopy(app_module.activities)
    initial_notifications = copy.deepcopy(app_module.notifications_log)
    initial_grades = copy.deepcopy(app_module.grades)

    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(initial_activities))
    app_module.notifications_log.clear()
    app_module.notifications_log.extend(copy.deepcopy(initial_notifications))
    app_module.grades.clear()
    app_module.grades.update(copy.deepcopy(initial_grades))

    yield

    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(initial_activities))
    app_module.notifications_log.clear()
    app_module.notifications_log.extend(copy.deepcopy(initial_notifications))
    app_module.grades.clear()
    app_module.grades.update(copy.deepcopy(initial_grades))


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app_module.app) as test_client:
        yield test_client


@pytest.fixture
def student_auth() -> tuple[str, str]:
    return ("michael@mergington.edu", "student123")


@pytest.fixture
def second_student_auth() -> tuple[str, str]:
    return ("emma@mergington.edu", "student123")


@pytest.fixture
def teacher_auth() -> tuple[str, str]:
    return ("teacher", "teacher123")
