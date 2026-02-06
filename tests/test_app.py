import copy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module

client = TestClient(app_module.app)
ORIGINAL_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities = copy.deepcopy(ORIGINAL_ACTIVITIES)
    yield


def test_get_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_participant():
    email = "newstudent@mergington.edu"
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    data = client.get("/activities").json()
    assert email in data["Chess Club"]["participants"]


def test_signup_rejects_duplicate():
    existing_email = ORIGINAL_ACTIVITIES["Chess Club"]["participants"][0]
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": existing_email},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant():
    email = ORIGINAL_ACTIVITIES["Soccer Team"]["participants"][0]
    response = client.delete(
        "/activities/Soccer%20Team/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    data = client.get("/activities").json()
    assert email not in data["Soccer Team"]["participants"]


def test_remove_participant_missing():
    response = client.delete(
        "/activities/Drama%20Club/participants",
        params={"email": "missing@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not registered"
