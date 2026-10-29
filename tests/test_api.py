from datetime import timedelta
from unittest.mock import patch
import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken
from accounts.models import LoginSession
from attendance.models import AttendanceRecord
from attendance.services import submit
from notifications.models import Notification
from django.core import mail

pytestmark = pytest.mark.django_db


def login(c, user="student"):
    return c.post(
        "/api/auth/login/", {"institute_id": user, "password": "Testing@9876"}, format="json"
    )


def marked(w):
    submit(w["faculty"], w["session"].pk, [{"student_id": w["student"].pk, "status": "A"}])
    return AttendanceRecord.objects.get()


@pytest.mark.parametrize(
    "url",
    [
        "admin/users/",
        "admin/courses/",
        "admin/sections/",
        "admin/timetable/",
        "admin/config/",
        "audit/",
        "admin/email-failures/",
        "sessions/today/",
        "reports/summary/",
    ],
)
def test_ST_SEC_04_student_forbidden(client, world, url):
    client.force_authenticate(world["student"])
    assert client.get("/api/" + url).status_code == 403


@pytest.mark.parametrize(
    "url", ["admin/users/", "audit/", "students/me/attendance/", "corrections/", "notifications/"]
)
def test_anonymous_denied(client, url):
    assert client.get("/api/" + url).status_code == 401


def test_IT_AUTH_03_expired_access(client, users):
    token = AccessToken(login(client).data["access"])
    token["exp"] = int((timezone.now() - timedelta(seconds=1)).timestamp())
    client.credentials(HTTP_AUTHORIZATION="Bearer " + str(token))
    assert client.get("/api/me/").status_code == 401


def test_IT_AUTH_04_logout_revokes_both(client, users):
    tokens = login(client).data
    client.credentials(HTTP_AUTHORIZATION="Bearer " + tokens["access"])
    assert client.get("/api/me/").status_code == 200
    assert client.post("/api/auth/logout/", {}, format="json").status_code == 205
    assert client.get("/api/me/").status_code == 401
    client.credentials()
    assert client.post("/api/auth/refresh/", {"refresh": tokens["refresh"]}).status_code == 401


def test_inactivity_timeout(client, users):
    token = login(client).data["access"]
    LoginSession.objects.update(last_seen=timezone.now() - timedelta(minutes=31))
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
    assert client.get("/api/me/").status_code == 401


def test_refresh_and_bad_token(client, users):
    tokens = login(client).data
    assert client.post("/api/auth/refresh/", {"refresh": tokens["refresh"]}).status_code == 200
    assert client.post("/api/auth/refresh/", {"refresh": "broken"}).status_code == 401


def test_IT_PWR_01_02_03_reset_endpoints(client, users):
    assert (
        client.post("/api/auth/password-reset/", {"email": users["student"].email}).status_code
        == 202
    )
    token = mail.outbox[-1].body.split("token=")[1]
    data = {"token": token, "new_password": "ChangedPass@987"}
    assert client.post("/api/auth/password-reset/confirm/", data).status_code == 200
    assert client.post("/api/auth/password-reset/confirm/", data).status_code == 410
    assert (
        client.post(
            "/api/auth/login/", {"institute_id": "student", "password": "ChangedPass@987"}
        ).status_code
        == 200
    )


def test_reset_weak_returns_400(client, users):
    client.post("/api/auth/password-reset/", {"email": users["student"].email})
    token = mail.outbox[-1].body.split("token=")[1]
    assert (
        client.post(
            "/api/auth/password-reset/confirm/", {"token": token, "new_password": "1"}
        ).status_code
        == 400
    )


@pytest.mark.parametrize(
    "payload", [{}, {"institute_id": "student", "password": ""}, {"password": "x"}]
)
def test_login_validation(client, users, payload):
    assert client.post("/api/auth/login/", payload, format="json").status_code == 400


def test_IT_ATT_01_02_session_marking_and_conflict(client, world):
    client.force_authenticate(world["faculty"])
    sessions = client.get("/api/sessions/today/").data
    assert sessions[0]["roster"][0]["srn"] == "student"
    url = f"/api/sessions/{world['session'].pk}/attendance/"
    data = {"records": [{"student_id": world["student"].pk, "status": "OD"}]}
    assert client.post(url, data, format="json").status_code == 201
    assert client.post(url, data, format="json").status_code == 409
    sessions = client.get("/api/sessions/today/").data
    assert sessions[0]["submitted"] and sessions[0]["roster"][0]["record_id"]


def test_IT_COR_01_02_approval_and_student_view(client, world):
    record = marked(world)
    client.force_authenticate(world["student"])
    assert client.get("/api/students/me/attendance/").data[0]["percentage"] == 0
    assert client.get("/api/students/me/records/").data[0]["id"] == record.pk
    response = client.post(
        "/api/corrections/",
        {"record_id": record.pk, "requested_status": "P", "reason": "Present"},
        format="json",
    )
    assert response.status_code == 201
    assert client.get("/api/corrections/").data[0]["reason"] == "Present"
    client.force_authenticate(world["faculty"])
    assert client.get("/api/corrections/").status_code == 200
    assert (
        client.patch(
            f"/api/corrections/{response.data['id']}/", {"decision": "APPROVE"}, format="json"
        ).status_code
        == 200
    )
    client.force_authenticate(world["student"])
    assert client.get("/api/students/me/attendance/").data[0]["percentage"] == 100


def test_IT_ADM_01_edit_and_audit_filters(client, world):
    record = marked(world)
    client.force_authenticate(world["admin"])
    assert (
        client.patch(
            f"/api/records/{record.pk}/", {"status": "P", "reason": "Verified"}, format="json"
        ).status_code
        == 200
    )
    url = f"/api/audit/?record={record.pk}&editor={world['admin'].pk}&from={timezone.localdate()}&to={timezone.localdate()}"
    result = client.get(url)
    assert result.data["count"] == 1 and result.data["results"][0]["old"] == "A"
    assert client.get("/api/audit/?page=invalid").status_code == 400
    assert client.delete("/api/audit/").status_code == 405
    assert client.get("/api/audit/?page=2").data["results"] == []


@pytest.mark.parametrize(
    "fmt,mime", [("csv", "text/csv"), ("pdf", "application/pdf"), ("json", "application/json")]
)
def test_IT_REP_01_02_exports(client, world, fmt, mime):
    marked(world)
    client.force_authenticate(world["faculty"])
    response = client.get("/api/reports/defaulters/?format=" + fmt)
    assert response.status_code == 200 and response["Content-Type"].startswith(mime)


def test_IT_CRS_01_02_03_admin_setup(client, world):
    client.force_authenticate(world["admin"])
    c = client.post("/api/admin/courses/", {"code": "CS200", "title": "DBMS"}, format="json")
    assert c.status_code == 201
    assert (
        client.post(
            "/api/admin/courses/", {"code": "CS200", "title": "Duplicate"}, format="json"
        ).status_code
        == 409
    )
    s = client.post(
        "/api/admin/sections/",
        {"course_id": c.data["id"], "faculty_id": world["faculty"].pk, "name": "E"},
        format="json",
    )
    assert s.status_code == 201
    assert (
        client.post(
            "/api/admin/sections/",
            {"course_id": c.data["id"], "faculty_id": world["student"].pk, "name": "X"},
            format="json",
        ).status_code
        == 404
    )
    slot = client.post(
        "/api/admin/timetable/",
        {"section_id": s.data["id"], "weekday": 0, "start": "15:00", "end": "16:00"},
        format="json",
    )
    assert slot.status_code == 201
    assert client.get("/api/admin/timetable/").data
    assert client.get("/api/admin/sections/").data
    assert client.get("/api/admin/courses/").data
    result = client.post(
        f"/api/admin/sections/{s.data['id']}/enroll/",
        {"csv": "institute_id\nstudent\nunknown\n"},
        format="json",
    )
    assert result.data["enrolled"] == 1 and len(result.data["errors"]) == 1


def test_IT_ADM_03_user_creation_and_roles(client, world):
    client.force_authenticate(world["admin"])
    data = {
        "institute_id": "NEW",
        "email": "new@example.test",
        "name": "New Student",
        "password": "InitialPass@987",
        "role": "STUDENT",
    }
    response = client.post("/api/admin/users/", data, format="json")
    assert response.status_code == 201 and "password" not in response.data
    assert (
        client.post("/api/admin/users/", dict(data, institute_id="NEW2"), format="json").status_code
        == 409
    )
    assert client.get("/api/admin/users/?q=NEW").data[0]["institute_id"] == "NEW"
    uid = response.data["id"]
    assert (
        client.patch(
            f"/api/admin/users/{uid}/", {"role": "FACULTY", "is_active": False}, format="json"
        ).status_code
        == 200
    )
    assert (
        client.patch(
            f"/api/admin/users/{world['admin'].pk}/", {"role": "STUDENT"}, format="json"
        ).status_code
        == 400
    )
    assert (
        client.patch(
            f"/api/admin/users/{world['faculty'].pk}/", {"role": "STUDENT"}, format="json"
        ).status_code
        == 409
    )
    assert (
        client.patch(
            f"/api/admin/users/{world['student'].pk}/", {"role": "ADMIN"}, format="json"
        ).status_code
        == 409
    )


def test_config_validation(client, world):
    client.force_authenticate(world["admin"])
    assert client.get("/api/admin/config/").data["threshold"] == 75
    assert (
        client.patch("/api/admin/config/", {"threshold": 80}, format="json").data["threshold"] == 80
    )
    assert client.patch("/api/admin/config/", {"threshold": 101}, format="json").status_code == 400


def test_notifications_scoped(client, world):
    n = Notification.objects.create(user=world["student"], message="Hello", key="hello")
    other = Notification.objects.create(user=world["faculty"], message="Private", key="private")
    client.force_authenticate(world["student"])
    assert len(client.get("/api/notifications/").data) == 1
    assert client.post(f"/api/notifications/{n.pk}/read/").data["read"]
    assert client.post(f"/api/notifications/{other.pk}/read/").status_code == 404
    client.force_authenticate(world["admin"])
    assert client.get("/api/admin/email-failures/").data == []


def test_csrf_browser_login_and_logout(world):
    client = APIClient(enforce_csrf_checks=True)
    assert (
        client.post(
            "/api/auth/login/", {"institute_id": "student", "password": "Testing@9876"}
        ).status_code
        == 403
    )
    assert client.get("/login/").status_code == 200
    token = client.cookies["csrftoken"].value
    assert (
        client.post(
            "/login/",
            {"institute_id": "student", "password": "Testing@9876"},
            HTTP_X_CSRFTOKEN=token,
        ).status_code
        == 302
    )
    assert client.get("/").status_code == 200
    assert client.get("/login/").status_code == 302
    assert client.get("/logout/").status_code == 405
    assert client.post("/logout/").status_code == 403
    assert (
        client.post("/logout/", HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value).status_code
        == 302
    )


def test_web_invalid_login_and_reset(client, users):
    assert (
        b"Invalid ID or password"
        in client.post("/login/", {"institute_id": "student", "password": "wrong"}).content
    )
    assert client.get("/reset/").status_code == 200
    assert client.get("/").status_code == 302


def test_health_redis_outage(client, settings):
    settings.CELERY_TASK_ALWAYS_EAGER = False
    import redis

    with patch("redis.Redis.ping", side_effect=redis.RedisError):
        assert client.get("/api/health/").status_code == 503


def test_unknown_records_and_malformed_json(client, world):
    client.force_authenticate(world["faculty"])
    assert (
        client.patch("/api/records/99999/", {"status": "P", "reason": "Check"}).status_code == 404
    )
    assert (
        client.post(
            "/api/corrections/", data="{broken", content_type="application/json"
        ).status_code
        == 400
    )


def test_roster_query_count_does_not_grow_per_student(client, world, django_assert_max_num_queries):
    from accounts.models import User
    from courses.models import Enrollment

    for i in range(60):
        s = User.objects.create_user(username=f"extra{i}", role="STUDENT")
        Enrollment.objects.create(section=world["section"], student=s)
    client.force_authenticate(world["faculty"])
    with django_assert_max_num_queries(12):
        assert len(client.get("/api/sessions/today/").data[0]["roster"]) == 61


@pytest.mark.parametrize("url", ["/api/auth/logout/", "/logout/"])
def test_cookie_logout_revokes_tokens_too(client, users, url):
    tokens = login(client).data
    response = client.post(url, {"refresh": tokens["refresh"]}, format="json")
    assert response.status_code in [205, 302]
    client.credentials(HTTP_AUTHORIZATION="Bearer " + tokens["access"])
    assert client.get("/api/me/").status_code == 401
    client.credentials()
    assert client.post("/api/auth/refresh/", {"refresh": tokens["refresh"]}).status_code == 401


def test_submitted_roster_preserves_actual_marks_after_new_enrollment(client, world):
    from accounts.models import User
    from courses.models import Enrollment

    marked(world)
    new = User.objects.create_user(username="late-enrollment", role="STUDENT")
    Enrollment.objects.create(section=world["section"], student=new)
    client.force_authenticate(world["faculty"])
    roster = client.get("/api/sessions/today/").data[0]["roster"]
    assert len(roster) == 1 and roster[0]["status"] == "A" and roster[0]["record_id"]
