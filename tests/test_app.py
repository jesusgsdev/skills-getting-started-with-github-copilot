"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities before each test"""
    activities.clear()
    activities.update({
        "Basketball Team": {
            "description": "Join our competitive basketball team and compete in league games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and participate in friendly matches",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 16,
            "participants": ["jessica@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["sarah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and develop acting skills",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["marcus@mergington.edu", "lucas@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills through competitive debate",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["rachel@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts through hands-on projects",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    })
    yield
    activities.clear()


class TestRoot:
    """Test root endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestActivitiesEndpoint:
    """Test the /activities endpoint"""
    
    def test_get_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Basketball Team" in data
        assert "Tennis Club" in data
        assert len(data) == 9

    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_activities_have_initial_participants(self, client):
        """Test that activities have initial participants"""
        response = client.get("/activities")
        data = response.json()
        
        assert len(data["Basketball Team"]["participants"]) == 1
        assert "alex@mergington.edu" in data["Basketball Team"]["participants"]
        assert len(data["Drama Club"]["participants"]) == 2


class TestSignupEndpoint:
    """Test the signup endpoint"""
    
    def test_successful_signup(self, client):
        """Test successful signup for an activity"""
        response = client.post("/activities/Basketball Team/signup?email=newstudent@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_updates_participants_list(self, client):
        """Test that signup actually adds participant to the list"""
        email = "newstudent@mergington.edu"
        client.post(f"/activities/Basketball Team/signup?email={email}")
        
        response = client.get("/activities")
        data = response.json()
        assert email in data["Basketball Team"]["participants"]

    def test_signup_nonexistent_activity(self, client):
        """Test signup for activity that doesn't exist"""
        response = client.post("/activities/Nonexistent Activity/signup?email=test@mergington.edu")
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_student(self, client):
        """Test that student can't signup for same activity twice"""
        email = "alex@mergington.edu"
        response = client.post(f"/activities/Basketball Team/signup?email={email}")
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_multiple_different_activities(self, client):
        """Test that a student can sign up for different activities"""
        email = "multiactivity@mergington.edu"
        
        response1 = client.post(f"/activities/Basketball Team/signup?email={email}")
        assert response1.status_code == 200
        
        response2 = client.post(f"/activities/Tennis Club/signup?email={email}")
        assert response2.status_code == 200
        
        response = client.get("/activities")
        data = response.json()
        assert email in data["Basketball Team"]["participants"]
        assert email in data["Tennis Club"]["participants"]


class TestUnregisterEndpoint:
    """Test the unregister endpoint"""
    
    def test_unregister_participant(self, client):
        """Test unregistering a participant from an activity"""
        email = "alex@mergington.edu"
        response = client.delete(f"/activities/Basketball Team/unregister?email={email}")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes participant"""
        email = "alex@mergington.edu"
        client.delete(f"/activities/Basketball Team/unregister?email={email}")
        
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Basketball Team"]["participants"]

    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from activity that doesn't exist"""
        response = client.delete("/activities/Nonexistent Activity/unregister?email=test@mergington.edu")
        assert response.status_code == 404

    def test_unregister_not_registered_student(self, client):
        """Test unregistering a student not in the activity"""
        response = client.delete("/activities/Basketball Team/unregister?email=notregistered@mergington.edu")
        assert response.status_code == 400

    def test_unregister_multiple_participants(self, client):
        """Test unregistering one of multiple participants"""
        # Drama Club has 2 participants
        response = client.get("/activities")
        initial_count = len(response.json()["Drama Club"]["participants"])
        assert initial_count == 2
        
        # Unregister one
        client.delete("/activities/Drama Club/unregister?email=marcus@mergington.edu")
        
        response = client.get("/activities")
        data = response.json()
        assert len(data["Drama Club"]["participants"]) == 1
        assert "lucas@mergington.edu" in data["Drama Club"]["participants"]
        assert "marcus@mergington.edu" not in data["Drama Club"]["participants"]
