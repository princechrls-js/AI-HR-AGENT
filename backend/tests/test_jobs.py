import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_jobs_public():
    response = client.get("/api/v1/jobs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
