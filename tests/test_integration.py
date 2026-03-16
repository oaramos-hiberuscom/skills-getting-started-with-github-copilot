import pytest


@pytest.mark.integration
def test_end_to_end_student_signup_then_teacher_grades_and_reads_results(client, student_auth, teacher_auth):
    # Arrange
    activity_name = "Science Club"

    # Act
    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "michael@mergington.edu"},
        auth=student_auth,
    )
    grade_response = client.put(
        f"/admin/activities/{activity_name}/grades",
        params={"email": "michael@mergington.edu"},
        json={"score": 92, "comments": "Strong progress"},
        auth=teacher_auth,
    )
    notifications_response = client.get("/notifications", auth=teacher_auth)
    grades_response = client.get(f"/admin/activities/{activity_name}/grades", auth=teacher_auth)

    # Assert
    assert signup_response.status_code == 200
    assert grade_response.status_code == 200
    assert notifications_response.status_code == 200
    assert grades_response.status_code == 200

    notifications = notifications_response.json()["notifications"]
    assert any(item["to"] == "michael@mergington.edu" for item in notifications)

    grades = grades_response.json()["grades"]
    assert grades["michael@mergington.edu"]["score"] == 92
