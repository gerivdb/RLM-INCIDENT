import pytest
from src.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["service"] == "rlm-incident"


def test_metrics(client):
    resp = client.get("/metrics")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "incidents" in data


def test_vote_success(client):
    resp = client.post("/vote", json={"choice": "yes"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["choice"] == "yes"


def test_vote_missing_choice(client):
    resp = client.post("/vote", json={})
    assert resp.status_code == 400


def test_create_incident(client):
    resp = client.post("/incidents", json={"title": "latency spike"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["status"] == "open"
    assert "id" in data


def test_create_incident_missing_title(client):
    resp = client.post("/incidents", json={})
    assert resp.status_code == 400


def test_close_incident(client):
    create = client.post("/incidents", json={"title": "db slow"}).get_json()
    incident_id = create["id"]
    resp = client.post(f"/incidents/{incident_id}/close")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "closed"


def test_close_incident_not_found(client):
    resp = client.post("/incidents/incident-999/close")
    assert resp.status_code == 404


def test_list_incidents(client):
    client.post("/incidents", json={"title": "incident-a"})
    resp = client.get("/incidents")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "incidents" in data
    assert len(data["incidents"]) >= 1


def test_status(client):
    resp = client.get("/status")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["service"] == "rlm-incident"
