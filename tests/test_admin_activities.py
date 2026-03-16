from src import app as app_module


def test_create_activity_success(client, teacher_auth):
    # Arrange
    payload = {
        "description": "Design and build robots",
        "schedule": "Fridays, 4:00 PM",
        "max_participants": 10,
        "participants": ["michael@mergington.edu"],
    }

    # Act
    response = client.post(
        "/admin/activities",
        params={"activity_name": "Robotics Club"},
        json=payload,
        auth=teacher_auth,
    )

    # Assert
    assert response.status_code == 200
    activities_response = client.get("/activities")
    assert "Robotics Club" in activities_response.json()


def test_create_activity_returns_409_for_duplicate_name(client, teacher_auth):
    # Arrange
    payload = {
        "description": "Duplicate",
        "schedule": "Any",
        "max_participants": 10,
        "participants": [],
    }

    # Act
    response = client.post(
        "/admin/activities",
        params={"activity_name": "Chess Club"},
        json=payload,
        auth=teacher_auth,
    )

    # Assert
    assert response.status_code == 409


def test_create_activity_returns_400_when_participants_exceed_capacity(client, teacher_auth):
    # Arrange
    payload = {
        "description": "Too many participants",
        "schedule": "Any",
        "max_participants": 1,
        "participants": ["michael@mergington.edu", "emma@mergington.edu"],
    }

    # Act
    response = client.post(
        "/admin/activities",
        params={"activity_name": "Small Club"},
        json=payload,
        auth=teacher_auth,
    )

    # Assert
    assert response.status_code == 400


def test_update_activity_returns_400_for_invalid_capacity_reduction(client, teacher_auth):
    # Arrange
    payload = {"max_participants": 1}

    # Act
    response = client.put(
        "/admin/activities/Chess%20Club",
        json=payload,
        auth=teacher_auth,
    )

    # Assert
    assert response.status_code == 400


def test_delete_activity_success_removes_activity_and_related_grades(client, teacher_auth):
    # Arrange
    grade_payload = {"score": 90, "comments": "Excellent"}
    grade_response = client.put(
        "/admin/activities/Chess%20Club/grades",
        params={"email": "michael@mergington.edu"},
        json=grade_payload,
        auth=teacher_auth,
    )
    assert grade_response.status_code == 200

    # Act
    delete_response = client.delete(
        "/admin/activities/Chess%20Club",
        auth=teacher_auth,
    )

    # Assert
    assert delete_response.status_code == 200
    assert "Chess Club" not in app_module.grades

    participants_response = client.get("/activities/Chess%20Club/participants")
    assert participants_response.status_code == 404


def test_delete_activity_returns_404_for_unknown_activity(client, teacher_auth):
    # Arrange

    # Act
    response = client.delete("/admin/activities/Unknown%20Club", auth=teacher_auth)

    # Assert
    assert response.status_code == 404
