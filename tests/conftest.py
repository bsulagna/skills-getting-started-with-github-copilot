import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


# Default test data
DEFAULT_ACTIVITIES = {
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
    },
    "Basketball Team": {
        "description": "Competitive basketball league and training",
        "schedule": "Tuesdays and Thursdays, 4:30 PM - 6:00 PM",
        "max_participants": 15,
        "participants": ["alex@mergington.edu"]
    },
    "Tennis Club": {
        "description": "Tennis lessons and tournament competitions",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 10,
        "participants": ["jessica@mergington.edu"]
    },
    "Art Studio": {
        "description": "Learn painting, drawing, and sculpture techniques",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["maya@mergington.edu", "lucas@mergington.edu"]
    },
    "Drama Club": {
        "description": "Acting, theater production, and performance",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 25,
        "participants": ["sarah@mergington.edu"]
    },
    "Debate Team": {
        "description": "Competitive debate and public speaking skills",
        "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["david@mergington.edu", "grace@mergington.edu"]
    },
    "Science Club": {
        "description": "Hands-on science experiments and research projects",
        "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
        "max_participants": 22,
        "participants": ["noah@mergington.edu"]
    }
}


@pytest.fixture
def client():
    """Provide a test client with fresh activities database for each test"""
    # Reset activities to default test data
    activities.clear()
    activities.update({k: {"description": v["description"],
                         "schedule": v["schedule"],
                         "max_participants": v["max_participants"],
                         "participants": v["participants"].copy()}
                      for k, v in DEFAULT_ACTIVITIES.items()})
    
    return TestClient(app)
