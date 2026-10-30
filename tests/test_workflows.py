"""Regression checks mapped to the submitted SAMS test plan."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def users():
    User = get_user_model()
    return {
        r: User.objects.create_user(
            username=r, password="Testing@9876", role=r.upper(), email=f"{r}@example.test"
        )
        for r in ["student", "faculty", "admin"]
    }


def test_IT_AUTH_01_login(client, users):
    r = client.post(
        "/api/auth/login/", {"institute_id": "student", "password": "Testing@9876"}, format="json"
    )
    assert r.status_code == 200
    assert r.data["role"] == "STUDENT"
    assert r.data["access"] and r.data["refresh"]


def test_UT_AUTH_03_lockout(client, users):
    for _ in range(5):
        client.post(
            "/api/auth/login/", {"institute_id": "student", "password": "wrong"}, format="json"
        )
    assert (
        client.post(
            "/api/auth/login/",
            {"institute_id": "student", "password": "Testing@9876"},
            format="json",
        ).status_code
        == 423
    )


def test_IT_AUTH_02_student_cannot_admin(client, users):
    client.force_authenticate(users["student"])
    assert client.get("/api/admin/users/").status_code == 403


def test_anonymous_health_only(client):
    assert client.get("/api/health/").status_code == 200
    assert client.get("/api/students/me/attendance/").status_code == 401
