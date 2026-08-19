def test_weekly_volume(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    client.post(
        "/workouts",
        headers=headers,
        json={
            "title": "Pull",
            "performed_on": "2026-08-18",
            "exercises": [
                {"name": "Pull up", "position": 0, "sets": [{"reps": 3, "external_load_kg": 20}, {"reps": 3, "external_load_kg": 20}]}
            ],
        },
    )
    response = client.get("/stats/weekly-volume", headers=headers)
    assert response.status_code == 200
    assert response.json()[0]["external_volume_kg"] == 120.0
