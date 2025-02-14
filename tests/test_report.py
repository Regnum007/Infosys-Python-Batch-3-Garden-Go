import pytest
from app import app  # Adjust import if needed

@pytest.fixture
def client():
    """Fixture to provide a test client."""
    with app.test_client() as client:
        yield client

# Test to check if the routes are correctly defined
def test_routes(client):
    with app.app_context():  # Ensures app context is available
        from flask import current_app
        # Print out the URL map for debugging
        print(current_app.url_map)
        # Check that the necessary routes are defined
        assert '/Report_issue' in [route.rule for route in current_app.url_map.iter_rules()]
        assert '/remove_issue/<int:issue_id>' in [route.rule for route in current_app.url_map.iter_rules()]

# Test to check if the report issue page renders correctly
def test_report_issue_page_render(client):
    """Test that the 'Report Issue' page renders successfully."""
    response = client.get('/Report_issue.html')  # Adjust route if necessary
    assert response.status_code == 200

# Test to check if submitting a report issue works correctly
def test_submit_report_issue(client):
    """Test that submitting a report issue works correctly."""
    form_data = {
        'order_id': '12345',
        'description': 'Test Issue Description'
    }
    response = client.post('/Report_issue.html', data=form_data)  # Adjust route if necessary
    assert response.status_code == 302
    assert response.location.endswith('Report_issue.html')  # Check redirection

    # Verify the issue was added to the database
    with app.app_context():
        from app import db, DeliveryIssue
        issue = DeliveryIssue.query.filter_by(order_id=12345).first()
        assert issue is not None
        assert issue.description == 'Test Issue Description'

# Test to check if removing an issue works correctly
def test_remove_issue(client):
    """Tests the removal of a reported issue."""
    issue_id = 1  # Example issue ID
    response = client.post(f'/remove_issue/{issue_id}')  # Adjust route if necessary
    assert response.status_code == 302

