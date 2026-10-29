"""Run only against your isolated synthetic demo; never against real student data."""

import os
from itertools import cycle
from locust import HttpUser, task, between


class FacultyUser(HttpUser):
    identities = cycle(f"FAC{i:03}" for i in range(1, 101))
    wait_time = between(1, 3)

    def on_start(self):
        self.client.get("/login/")
        csrf = self.client.cookies.get("csrftoken")
        self.client.post(
            "/api/auth/login/",
            json={
                "institute_id": os.getenv("LOAD_USER") or next(self.identities),
                "password": os.getenv("DEMO_PASSWORD", "DemoPass@1234"),
            },
            headers={"X-CSRFToken": csrf},
        )

    @task(3)
    def dashboard(self):
        self.client.get("/api/sessions/today/")

    @task(1)
    def report(self):
        self.client.get("/api/reports/summary/")
