import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities(client):
    # Arrange: No special setup needed as activities are predefined

    # Act: Make GET request to /activities
    response = client.get("/activities")

    # Assert: Check status and response structure
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "description" in data["Chess Club"]
    assert "participants" in data["Chess Club"]


def test_signup_success(client):
    # Arrange: Choose an activity and new email
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act: Make POST request to signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Check success response and data update
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    # Verify email added to participants
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate(client):
    # Arrange: Sign up first
    activity_name = "Programming Class"
    email = "duplicate@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act: Try to sign up again
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Check 400 error
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_invalid_activity(client):
    # Arrange: Invalid activity name
    activity_name = "Invalid Activity"
    email = "test@mergington.edu"

    # Act: Make POST request
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Check 404 error
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_unregister_success(client):
    # Arrange: Sign up first
    activity_name = "Gym Class"
    email = "removeme@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act: Make DELETE request
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Check success and removal
    assert response.status_code == 200
    assert "Unregistered" in response.json()["message"]
    # Verify email removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email not in activities[activity_name]["participants"]


def test_unregister_not_enrolled(client):
    # Arrange: Activity and email not enrolled
    activity_name = "Drama Club"
    email = "notenrolled@mergington.edu"

    # Act: Make DELETE request
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Check 400 error
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"]


def test_unregister_invalid_activity(client):
    # Arrange: Invalid activity
    activity_name = "Invalid Activity"
    email = "test@mergington.edu"

    # Act: Make DELETE request
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Check 404 error
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_root_redirect(client):
    # Arrange: No setup

    # Act: Make GET request to /
    response = client.get("/", follow_redirects=False)

    # Assert: Check redirect to /static/index.html
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"