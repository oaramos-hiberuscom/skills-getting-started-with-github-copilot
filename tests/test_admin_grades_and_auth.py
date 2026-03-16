import pytest


@pytest.mark.auth
def test_get_notifications_requires_teacher_auth(client):
    # Arrange

    # Act
    response = client.get("/notifications")

    # Assert
    assert response.status_code == 401


@pytest.mark.auth
def test_get_notifications_rejects_student_credentials(client, student_auth):
    # Arrange

    # Act
    response = client.get("/notifications", auth=student_auth)

    # Assert
    assert response.status_code == 401


def test_get_notifications_returns_entries_for_teacher(client, student_auth, teacher_auth):
    # Arrange
    signup_response = client.post(
        "/activities/Science%20Club/signup",
        params={"email": "michael@mergington.edu"},
        auth=student_auth,
    )
    assert signup_response.status_code == 200

    # Act
    response = client.get("/notifications", auth=teacher_auth)

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert payload["requested_by"] == "teacher"
    assert len(payload["notifications"]) >= 1


def test_put_grade_success_and_get_grades_returns_saved_result(client, teacher_auth):
    # Arrange
    payload = {"score": 85.5, "comments": "Great participation"}

    # Act
    put_response = client.put(
        "/admin/activities/Chess%20Club/grades",
        params={"email": "michael@mergington.edu"},
        json=payload,
        auth=teacher_auth,
    )

    # Assert
    assert put_response.status_code == 200

    get_response = client.get("/admin/activities/Chess%20Club/grades", auth=teacher_auth)
    assert get_response.status_code == 200
    grades_payload = get_response.json()["grades"]
    assert grades_payload["michael@mergington.edu"]["score"] == 85.5


def test_put_grade_returns_404_for_student_not_registered(client, teacher_auth):
    # Arrange
    payload = {"score": 70, "comments": "Attempted grading"}

    # Act
    response = client.put(
        "/admin/activities/Programming%20Class/grades",
        params={"email": "michael@mergington.edu"},
        json=payload,
        auth=teacher_auth,
    )

    # Assert
    assert response.status_code == 404


def test_get_grades_returns_404_for_unknown_activity(client, teacher_auth):
    # Arrange

    # Act
    response = client.get("/admin/activities/Unknown%20Club/grades", auth=teacher_auth)

    # Assert
    assert response.status_code == 404
