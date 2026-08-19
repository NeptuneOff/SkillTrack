import json
import time
import urllib.error
import urllib.request

API = "http://localhost:8000"


def request(path: str, method: str = "GET", data: dict | None = None, token: str | None = None):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(API + path, data=body, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode() or "{}")


for _ in range(60):
    try:
        if request("/health")["status"] == "ok":
            break
    except Exception:
        time.sleep(2)
else:
    raise SystemExit("API healthcheck failed")

user = {"email": "demo@skilltrack.local", "password": "DemoPassword123!", "display_name": "Demo"}
try:
    request("/auth/register", "POST", user)
except urllib.error.HTTPError as exc:
    if exc.code != 409:
        raise

token = request("/auth/login", "POST", {"email": user["email"], "password": user["password"]})["access_token"]
request("/workouts", "POST", {"title": "Smoke test", "performed_on": "2026-08-18", "exercises": []}, token)
workouts = request("/workouts", token=token)
if not workouts:
    raise SystemExit("Smoke test failed: no workout returned")
print("Smoke test OK")
