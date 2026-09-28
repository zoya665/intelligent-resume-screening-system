"""
Unit and Integration tests for FastAPI endpoints.
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


def test_skill_taxonomy():
    response = client.get("/api/skill-taxonomy")
    assert response.status_code == 200
    data = response.json()
    assert "Programming Languages" in data
    assert "AI / ML / Data Science" in data


def test_screen_single_endpoint():
    payload = {
        "resume_text": "John Doe. Experienced Python engineer with Scikit-learn, NLP, Pandas, and FastAPI.",
        "job_description": {
            "title": "AI Engineer",
            "description": "Seeking Python engineer with Scikit-learn, NLP, and FastAPI.",
            "required_skills": ["python", "scikit-learn", "fastapi"],
            "required_experience": 2.0
        }
    }
    response = client.post("/api/screen-single", json=payload)
    assert response.status_code == 200
    res_json = response.json()
    assert "composite_score" in res_json
    assert res_json["composite_score"] > 50.0
    assert "skill_gap_analysis" in res_json
