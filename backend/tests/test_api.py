import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope='module')
def client():
    with TestClient(app) as test_client:
        yield test_client


def token(client: TestClient):
    r = client.post('/auth/login', json={'email':'demo@skilltrack.dev','password':'DemoPassword123!'})
    assert r.status_code == 200, r.text
    return r.json()['access_token']


def test_health(client: TestClient):
    assert client.get('/health').json()['status'] == 'ok'


def test_login_dashboard_workout(client: TestClient):
    headers={'Authorization': f'Bearer {token(client)}'}
    r = client.get('/dashboard', headers=headers)
    assert r.status_code == 200
    payload = {'title':'Test séance','date':'2026-08-19','type':'Test','intensity':5,'duration_minutes':45,'notes':'pytest','sets':[{'exercise':'Push-up','reps':10,'load_kg':0,'duration_seconds':0,'difficulty':5,'notes':''}]}
    r = client.post('/workouts', json=payload, headers=headers)
    assert r.status_code == 200
    wid = r.json()['id']
    assert client.get(f'/workouts/{wid}', headers=headers).status_code == 200
    assert client.delete(f'/workouts/{wid}', headers=headers).status_code == 200

def test_protected_routes_require_a_token(client: TestClient):
    for path in ('/dashboard', '/workouts', '/goals', '/exports/json', '/imports/history'):
        assert client.get(path).status_code in (401, 403)

def test_goal_crud(client: TestClient):
    headers = {'Authorization': f'Bearer {token(client)}'}
    payload = {'skill':'Full planche test','goal_type':'figure','target':'Tenir 5 secondes','current_level':'Straddle','current_value':2,'target_value':5,'unit':'secondes','priority':'haute','notes':'objectif pytest','status':'actif','deadline':None,'is_done':False}
    created = client.post('/goals', json=payload, headers=headers)
    assert created.status_code == 200, created.text
    goal_id = created.json()['id']
    payload.update({'current_value':5, 'status':'termine', 'is_done':True})
    updated = client.put(f'/goals/{goal_id}', json=payload, headers=headers)
    assert updated.status_code == 200
    assert updated.json()['is_done'] is True
    assert client.delete(f'/goals/{goal_id}', headers=headers).status_code == 200

def test_import_report_and_exports(client: TestClient):
    headers = {'Authorization': f'Bearer {token(client)}'}
    csv_data = 'date,title,exercise,reps,difficulty\n2026-08-19,Import pytest,Pull-up,5,6\ninvalide,Ligne rejetee,Dips,8,7\n'
    result = client.post('/imports/csv', files={'file': ('workouts.csv', csv_data, 'text/csv')}, headers=headers)
    assert result.status_code == 200, result.text
    assert result.json()['imported_rows'] == 1
    assert result.json()['rejected_rows'] == 1
    assert client.get('/imports/history', headers=headers).status_code == 200
    json_export = client.get('/exports/json', headers=headers)
    assert json_export.status_code == 200
    assert 'attachment' in json_export.headers['content-disposition']
    assert client.get('/exports/csv', headers=headers).status_code == 200
    for workout in client.get('/workouts', headers=headers).json():
        if workout['title'] == 'Import pytest':
            assert client.delete(f"/workouts/{workout['id']}", headers=headers).status_code == 200

def test_invalid_csv_has_a_clear_error(client: TestClient):
    headers = {'Authorization': f'Bearer {token(client)}'}
    result = client.post('/imports/csv', files={'file': ('invalid.csv', 'foo,bar\n1,2\n', 'text/csv')}, headers=headers)
    assert result.status_code == 422
    assert 'Colonnes obligatoires' in result.json()['detail']
