def test_create_and_list_workout(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/workouts",
        headers=headers,
        json={
            "title": "Push statics",
            "performed_on": "2026-08-18",
            "notes": "Planche focus",
            "exercises": [
                {
                    "name": "Planche lean",
                    "variation": "parallettes",
                    "position": 0,
                    "sets": [{"reps": 5, "external_load_kg": 0, "hold_seconds": 12, "rpe": 7}],
                }
            ],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Push statics"
    assert data["exercises"][0]["sets"][0]["hold_seconds"] == 12

    listing = client.get("/workouts", headers=headers)
    assert listing.status_code == 200
    assert len(listing.json()) == 1


def test_user_cannot_access_other_user_workout(client):
    first = {"email": "first@example.com", "password": "StrongPassword123", "display_name": "First"}
    second = {"email": "second@example.com", "password": "StrongPassword123", "display_name": "Second"}
    client.post("/auth/register", json=first)
    client.post("/auth/register", json=second)
    token1 = client.post("/auth/login", json={"email": first["email"], "password": first["password"]}).json()["access_token"]
    token2 = client.post("/auth/login", json={"email": second["email"], "password": second["password"]}).json()["access_token"]
    created = client.post("/workouts", headers={"Authorization": f"Bearer {token1}"}, json={"title": "Private", "performed_on": "2026-08-18", "exercises": []}).json()

    forbidden = client.get(f"/workouts/{created['id']}", headers={"Authorization": f"Bearer {token2}"})
    assert forbidden.status_code == 404
