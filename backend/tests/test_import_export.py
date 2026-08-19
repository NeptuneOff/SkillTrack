def test_import_csv_and_export_json(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    csv_content = "date,workout_title,exercise,reps,external_load_kg,hold_seconds,rpe\n2026-08-18,Push,Weighted dips,5,40,,8\n2026-08-18,Push,Planche lean,3,0,12,7\n"
    response = client.post(
        "/imports/workouts",
        headers=headers,
        files={"file": ("workouts.csv", csv_content.encode("utf-8"), "text/csv")},
    )
    assert response.status_code == 200
    assert response.json()["rows_accepted"] == 2

    exported = client.get("/exports/workouts.json", headers=headers)
    assert exported.status_code == 200
    assert exported.json()["workouts"][0]["title"] == "Push"


def test_import_rejects_invalid_rows(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    csv_content = "date,workout_title,exercise,reps,external_load_kg\nnot-a-date,Push,Dips,5,40\n"
    response = client.post(
        "/imports/workouts",
        headers=headers,
        files={"file": ("bad.csv", csv_content.encode("utf-8"), "text/csv")},
    )
    assert response.status_code == 200
    assert response.json()["rows_rejected"] == 1
    assert response.json()["errors"][0]["error"] == "invalid_date"
