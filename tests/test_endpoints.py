import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities

    def test_get_activities_includes_activity_details(self, client):
        """Test that returned activities include all required fields"""
        response = client.get("/activities")
        activities = response.json()
        chess_club = activities["Chess Club"]
        
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club

    def test_get_activities_includes_existing_participants(self, client):
        """Test that activities include their current participants"""
        response = client.get("/activities")
        activities = response.json()
        chess_club = activities["Chess Club"]
        
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestRootRedirect:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static_index(self, client):
        """Test that GET / redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant_success(self, client):
        """Test successfully signing up a new participant"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds the participant to the activity"""
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        
        # Verify participant was added
        response = client.get("/activities")
        activities = response.json()
        chess_club = activities["Chess Club"]
        assert "newstudent@mergington.edu" in chess_club["participants"]
        assert len(chess_club["participants"]) == 3

    def test_signup_for_nonexistent_activity_returns_404(self, client):
        """Test that signing up for a non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_email_is_allowed(self, client):
        """Test that signing up with a duplicate email is currently allowed"""
        # This documents current behavior - duplicate registrations are allowed
        participant = "michael@mergington.edu"
        response = client.post(
            f"/activities/Chess Club/signup?email={participant}"
        )
        assert response.status_code == 200
        
        # Verify duplicate was added
        response = client.get("/activities")
        activities = response.json()
        chess_club = activities["Chess Club"]
        count = sum(1 for p in chess_club["participants"] if p == participant)
        assert count == 2

    def test_signup_multiple_different_activities_same_student(self, client):
        """Test that a student can sign up for multiple different activities"""
        student_email = "newstudent@mergington.edu"
        
        # Sign up for Chess Club
        response1 = client.post(
            f"/activities/Chess Club/signup?email={student_email}"
        )
        assert response1.status_code == 200
        
        # Sign up for Programming Class
        response2 = client.post(
            f"/activities/Programming Class/signup?email={student_email}"
        )
        assert response2.status_code == 200
        
        # Verify student is in both activities
        response = client.get("/activities")
        activities = response.json()
        assert student_email in activities["Chess Club"]["participants"]
        assert student_email in activities["Programming Class"]["participants"]

    def test_signup_preserves_other_activities(self, client):
        """Test that signing up for one activity doesn't affect others"""
        # Get initial state of Programming Class
        response = client.get("/activities")
        initial_activities = response.json()
        initial_programming = initial_activities["Programming Class"]["participants"].copy()
        
        # Sign up for Chess Club
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        
        # Verify Programming Class is unchanged
        response = client.get("/activities")
        final_activities = response.json()
        assert final_activities["Programming Class"]["participants"] == initial_programming


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""

    def test_remove_existing_participant_success(self, client):
        """Test successfully removing an existing participant"""
        response = client.delete(
            "/activities/Chess Club/participants/michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_remove_participant_actually_removes_them(self, client):
        """Test that the participant is actually removed from the activity"""
        client.delete(
            "/activities/Chess Club/participants/michael@mergington.edu"
        )
        
        # Verify participant was removed
        response = client.get("/activities")
        activities = response.json()
        chess_club = activities["Chess Club"]
        assert "michael@mergington.edu" not in chess_club["participants"]
        assert len(chess_club["participants"]) == 1

    def test_remove_nonexistent_participant_returns_404(self, client):
        """Test that removing a non-existent participant returns 404"""
        response = client.delete(
            "/activities/Chess Club/participants/nonexistent@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]

    def test_remove_from_nonexistent_activity_returns_404(self, client):
        """Test that removing from a non-existent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent Club/participants/student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_remove_second_duplicate_removes_only_one(self, client):
        """Test that removing when duplicates exist removes only one instance"""
        # First sign up the same person twice
        participant = "test@mergington.edu"
        client.post(f"/activities/Chess Club/signup?email={participant}")
        client.post(f"/activities/Chess Club/signup?email={participant}")
        
        # Verify duplicates exist
        response = client.get("/activities")
        count = sum(1 for p in response.json()["Chess Club"]["participants"] 
                   if p == participant)
        assert count == 2
        
        # Remove one instance
        response = client.delete(
            f"/activities/Chess Club/participants/{participant}"
        )
        assert response.status_code == 200
        
        # Verify only one was removed
        response = client.get("/activities")
        count = sum(1 for p in response.json()["Chess Club"]["participants"] 
                   if p == participant)
        assert count == 1

    def test_remove_preserves_other_participants(self, client):
        """Test that removing one participant doesn't affect others"""
        # Get initial state
        response = client.get("/activities")
        initial_participants = response.json()["Chess Club"]["participants"].copy()
        
        # Remove one participant
        client.delete(
            "/activities/Chess Club/participants/michael@mergington.edu"
        )
        
        # Verify the other participant is still there
        response = client.get("/activities")
        remaining = response.json()["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in remaining

    def test_remove_preserves_other_activities(self, client):
        """Test that removing from one activity doesn't affect others"""
        # Get initial state of Programming Class
        response = client.get("/activities")
        initial_activities = response.json()
        initial_programming = initial_activities["Programming Class"]["participants"].copy()
        
        # Remove from Chess Club
        client.delete(
            "/activities/Chess Club/participants/michael@mergington.edu"
        )
        
        # Verify Programming Class is unchanged
        response = client.get("/activities")
        final_activities = response.json()
        assert final_activities["Programming Class"]["participants"] == initial_programming


class TestIntegrationScenarios:
    """Integration tests combining multiple operations"""

    def test_signup_and_remove_workflow(self, client):
        """Test complete workflow: signup and then remove"""
        email = "workflow@mergington.edu"
        activity = "Chess Club"
        
        # Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify signed up
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Remove
        response = client.delete(f"/activities/{activity}/participants/{email}")
        assert response.status_code == 200
        
        # Verify removed
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]

    def test_multiple_signups_and_removes(self, client):
        """Test multiple sequential signup and remove operations"""
        activity = "Tennis Club"
        emails = ["student1@test.edu", "student2@test.edu", "student3@test.edu"]
        
        # Sign up multiple students
        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all signed up
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        for email in emails:
            assert email in participants
        
        # Remove one student
        response = client.delete(f"/activities/{activity}/participants/{emails[1]}")
        assert response.status_code == 200
        
        # Verify only that one was removed
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert emails[0] in participants
        assert emails[1] not in participants
        assert emails[2] in participants

    def test_activity_state_isolation_between_tests(self, client):
        """Test that each test gets fresh activities (implicit through fixture)"""
        # Each call to client fixture provides fresh data
        response = client.get("/activities")
        chess_club = response.json()["Chess Club"]
        
        # Should have original participants, not modified from previous tests
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
