def test_signup_success_adds_student_and_creates_notification(client, teacher_auth):
    # Arrange
    activity_name = "Science Club"
    auth = ("michael@mergington.edu", "student123")

    # Act
    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "michael@mergington.edu"},
        auth=auth,
    )

    # Assert
    assert signup_response.status_code == 200
    participants_response = client.get(f"/activities/{activity_name}/participants")
    participants_payload = participants_response.json()
    assert "michael@mergington.edu" in participants_payload["participants"]

    notifications_response = client.get("/notifications", auth=teacher_auth)
    notifications_payload = notifications_response.json()["notifications"]
    assert any(item["to"] == "michael@mergington.edu" for item in notifications_payload)


def test_signup_returns_409_when_student_already_registered(client, student_auth):
    # Arrange

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "michael@mergington.edu"},
        auth=student_auth,
    )

    # Assert
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]


def test_signup_returns_403_when_authenticated_student_uses_another_email(client, student_auth):
    # Arrange

    # Act
    response = client.post(
        "/activities/Science%20Club/signup",
        params={"email": "emma@mergington.edu"},
        auth=student_auth,
    )

    # Assert
    assert response.status_code == 403


def test_signup_returns_400_when_activity_is_full(client, teacher_auth, second_student_auth):
    # Arrange
    create_payload = {
        "description": "Limited seats",
        "schedule": "Monday 5PM",
        "max_participants": 1,
        "participants": ["michael@mergington.edu"],
    }
    client.post(
        "/admin/activities",
        params={"activity_name": "Tiny Club"},
        json=create_payload,
        auth=teacher_auth,
    )

    # Act
    response = client.post(
        "/activities/Tiny%20Club/signup",
        params={"email": "emma@mergington.edu"},
        auth=second_student_auth,
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Tiny Club is full"


def test_signup_returns_404_for_unknown_activity(client, student_auth):
    # Arrange

    # Act
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": "michael@mergington.edu"},
        auth=student_auth,
    )

    # Assert
    assert response.status_code == 404


def test_cancel_signup_success_removes_student(client, student_auth):
    # Arrange
    client.post(
        "/activities/Science%20Club/signup",
        params={"email": "michael@mergington.edu"},
        auth=student_auth,
    )

    # Act
    response = client.delete(
        "/activities/Science%20Club/signup",
        params={"email": "michael@mergington.edu"},
        auth=student_auth,
    )

    # Assert
    assert response.status_code == 200
    participants_response = client.get("/activities/Science%20Club/participants")
    assert "michael@mergington.edu" not in participants_response.json()["participants"]


def test_cancel_signup_returns_404_when_student_not_registered(client, student_auth):
    # Arrange

    # Act
    response = client.delete(
        "/activities/Programming%20Class/signup",
        params={"email": "michael@mergington.edu"},
        auth=student_auth,
    )

    # Assert
    assert response.status_code == 404


def test_cancel_signup_returns_403_for_mismatched_email(client, student_auth):
    # Arrange

    # Act
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": "emma@mergington.edu"},
        auth=student_auth,
    )

    # Assert
    assert response.status_code == 403
