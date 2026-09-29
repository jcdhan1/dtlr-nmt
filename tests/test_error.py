import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_translate_missing_fields(client):
    """Ensure the API returns a 400 error if JSON payload is missing data"""
    response = client.post('/translate', json={})
    assert response.status_code == 400
    assert b"Missing required fields" in response.data

