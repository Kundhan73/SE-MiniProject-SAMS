"""Isolated synthetic acceptance workload; includes auth, reports and real marking."""

import os
import json
import time
from pathlib import Path
from itertools import cycle
import gevent
from locust import HttpUser, task, between, events
from locust.exception import StopUser

identities = cycle(f"FAC{i:03}" for i in range(1, 101))
claimed = set()
profile = os.getenv("VALIDATION_PROFILE", "perf100")
duration = int(os.getenv("VALIDATION_SECONDS", "600"))
meta = {
    "profile": profile,
    "configured_seconds_after_full_spawn": duration,
    "login_successes": 0,
    "mark_successes": 0,
    "expected_duplicate_conflicts": 0,
    "start_monotonic": None,
    "finish_monotonic": None,
    "users_spawned": 0,
}
environment = None


@events.init.add_listener
def init(environment: object, **kwargs):
    globals()["environment"] = environment


@events.spawning_complete.add_listener
def started(user_count, **kwargs):
    if meta["start_monotonic"] is not None:
        return
    meta["users_spawned"] = user_count
    meta["start_monotonic"] = time.monotonic()
    meta["started_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    meta["minimum_active_users_during_measured_period"] = user_count

    def observe():
        deadline = meta["start_monotonic"] + duration
        while time.monotonic() < deadline:
            meta["minimum_active_users_during_measured_period"] = min(
                meta["minimum_active_users_during_measured_period"], environment.runner.user_count
            )
            gevent.sleep(1)

    gevent.spawn(observe)
    gevent.spawn_later(duration, environment.runner.quit)


@events.test_stop.add_listener
def finished(environment, **kwargs):
    meta["finish_monotonic"] = time.monotonic()
    meta["finished_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    if meta["start_monotonic"]:
        meta["measured_seconds_after_full_spawn"] = (
            meta["finish_monotonic"] - meta["start_monotonic"]
        )
    Path("/evidence/" + profile + "-duration.json").write_text(json.dumps(meta, indent=2))


class FacultyAcceptance(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.identity = next(identities)
        self.client.get("/login/", name="GET login page")
        with self.client.post(
            "/api/auth/login/",
            json={"institute_id": self.identity, "password": "DemoPass@1234"},
            headers={"X-CSRFToken": self.client.cookies.get("csrftoken", "")},
            catch_response=True,
            name="POST faculty login",
        ) as response:
            if response.status_code != 200:
                response.failure("Login failed: HTTP " + str(response.status_code))
                raise StopUser()
        meta["login_successes"] += 1

    @task(3)
    def dashboard(self):
        self.client.get("/api/sessions/today/", name="GET current sessions and roster")

    @task(2)
    def report(self):
        self.client.get("/api/reports/summary/", name="GET attendance summary")

    @task(1)
    def marking(self):
        response = self.client.get("/api/sessions/today/", name="GET current sessions and roster")
        if response.status_code != 200:
            return
        for session in response.json():
            key = session["session_id"]
            if session["submitted"] or key in claimed:
                continue
            claimed.add(key)
            records = [
                {"student_id": row["student_id"], "status": ("P", "A", "OD")[i % 3]}
                for i, row in enumerate(session["roster"])
            ]
            with self.client.post(
                f"/api/sessions/{key}/attendance/",
                json={"records": records},
                headers={"X-CSRFToken": self.client.cookies.get("csrftoken", "")},
                catch_response=True,
                name="POST complete attendance roster",
            ) as result:
                if result.status_code == 201:
                    meta["mark_successes"] += 1
                elif result.status_code == 409:
                    meta["expected_duplicate_conflicts"] += 1
                    result.success()
