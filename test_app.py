import pytest
import time
from app import app, missions

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_start_mission(client):
    resp = client.post('/fly', json={'waypoints': [[1,2,3], [4,5,6]]})
    assert resp.status_code == 202
    data = resp.get_json()
    mission_id = data['mission_id']
    assert mission_id in missions

def test_mission_complete(client):
    resp = client.post('/fly', json={'waypoints': [[1,2,3], [4,5,6]]})
    assert resp.status_code == 202
    mission_id = resp.get_json()['mission_id']   # fixed spelling

    # Poll status until completed or timeout
    for _ in range(10):  # wait up to 10 seconds
        status_resp = client.get(f'/status/{mission_id}')   # fixed: assign response
        assert status_resp.status_code == 200
        status_data = status_resp.get_json()
        if status_data['status'] == 'completed':
            break
        time.sleep(1)
    else:
        # This runs only if the loop didn't break (timeout)
        assert False, "Mission did not complete in time"

    # Verify final status (only reached if loop broke)
    assert status_data['status'] == 'completed'
    assert missions[mission_id]['progress'] == 2