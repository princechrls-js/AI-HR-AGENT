import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_apply_no_auth():
    response = client.post("/api/v1/applications/apply?job_id=1")
    assert response.status_code == 401
