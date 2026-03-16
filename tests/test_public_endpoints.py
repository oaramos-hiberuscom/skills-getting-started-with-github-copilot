def test_root_redirects_to_static_index(client):
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_available_activities(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["max_participants"] == 12


def test_get_activity_participants_returns_counts(client):
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.get(f"/activities/{activity_name}/participants")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert payload["activity"] == activity_name
    assert payload["count"] == len(payload["participants"])


def test_get_activity_participants_returns_404_for_unknown_activity(client):
    # Arrange

    # Act
    response = client.get("/activities/Unknown%20Club/participants")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
