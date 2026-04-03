import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
import os

# Use a separate test database or SQLite for simple testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test.db"):
        os.remove("./test.db")

def test_signup_and_login():
    # Test Signup
    response = client.post(
        "/api/v1/auth/signup",
        json={"name": "Test HR", "email": "hr@test.com", "password": "password123", "role": "hr"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "hr@test.com"

    # Test Login
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "hr@test.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_create_job_requires_hr():
    # Signup as candidate
    client.post(
        "/api/v1/auth/signup",
        json={"name": "Test Candidate", "email": "can@test.com", "password": "password123", "role": "candidate"}
    )
    
    # Login
    login_res = client.post(
        "/api/v1/auth/login",
        data={"username": "can@test.com", "password": "password123"}
    )
    token = login_res.json()["access_token"]
    
    # Try to create job
    response = client.post(
        "/api/v1/hr/jobs",
        json={
            "title": "Software Engineer",
            "company_name": "AI Tech",
            "location": "Remote",
            "employment_type": "Full-time",
            "experience_required": "3+ years",
            "skills_required": "Python, FastAPI",
            "job_description": "We are looking for a dev..."
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
