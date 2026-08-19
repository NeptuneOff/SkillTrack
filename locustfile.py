from locust import HttpUser, between, task


class SkillTrackUser(HttpUser):
    wait_time = between(1, 3)
    token = ""

    def on_start(self):
        self.client.post("/auth/register", json={"email": "load@example.com", "password": "DemoPassword123!", "display_name": "Load"})
        response = self.client.post("/auth/login", json={"email": "load@example.com", "password": "DemoPassword123!"})
        self.token = response.json().get("access_token", "")

    @task(3)
    def list_workouts(self):
        self.client.get("/workouts", headers={"Authorization": f"Bearer {self.token}"})

    @task(1)
    def stats(self):
        self.client.get("/stats/weekly-volume", headers={"Authorization": f"Bearer {self.token}"})
