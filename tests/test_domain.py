from datetime import timedelta
from unittest.mock import patch
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.core import mail
import pytest
from accounts import services as auth
from accounts.models import User, LoginSession, ResetToken
from attendance import services as att
from attendance.models import AttendanceRecord
from courses import services as courses
from courses.models import Course, Section, Enrollment
from reports.services import attendance_report, export_report, threshold_value
from audit.models import AuditLog
from notifications.models import Notification
from notifications.tasks import nightly_scan, notify, deliver_email
from core.errors import DomainError

pytestmark = pytest.mark.django_db


def mark(w, status="A"):
    att.submit(w["faculty"], w["session"].pk, [{"student_id": w["student"].pk, "status": status}])
    return AttendanceRecord.objects.get(session=w["session"])


def reset_token(user):
    auth.request_reset(user.email)
    return mail.outbox[-1].body.split("token=")[1]


def test_UT_AUTH_02_counter(users):
    with pytest.raises(DomainError):
        auth.authenticate("student", "wrong")
    users["student"].refresh_from_db()
    assert users["student"].failed_attempts == 1


def test_UT_AUTH_04_expired_lock(users):
    u = users["student"]
    u.failed_attempts = 5
    u.locked_until = timezone.now() - timedelta(seconds=1)
    u.save()
    user, _ = auth.authenticate("student", "Testing@9876")
    assert user.failed_attempts == 0 and user.locked_until is None


@pytest.mark.parametrize("username,password", [("", "pass"), ("student", ""), ("unknown", "x")])
def test_UT_AUTH_05_invalid(users, username, password):
    with pytest.raises(DomainError):
        auth.authenticate(username, password)


def test_inactive_cannot_login(users):
    u = users["student"]
    u.is_active = False
    u.save()
    with pytest.raises(DomainError):
        auth.authenticate("student", "Testing@9876")


def test_UT_PWR_01_hashed_token(users):
    raw = reset_token(users["student"])
    item = ResetToken.objects.get()
    assert item.digest != raw and item.expires_at > timezone.now() + timedelta(minutes=29)


def test_UT_PWR_02_expiry(users):
    raw = reset_token(users["student"])
    ResetToken.objects.update(expires_at=timezone.now() - timedelta(seconds=1))
    with pytest.raises(DomainError):
        auth.confirm_reset(raw, "NewPassword@123")


def test_UT_PWR_03_single_use_and_revocation(users):
    auth.authenticate("student", "Testing@9876")
    raw = reset_token(users["student"])
    auth.confirm_reset(raw, "NewPassword@123")
    assert not LoginSession.objects.filter(active=True).exists()
    with pytest.raises(DomainError):
        auth.confirm_reset(raw, "NewPassword@123")


def test_UT_PWR_04_weak_password(users):
    raw = reset_token(users["student"])
    from django.core.exceptions import ValidationError

    with pytest.raises(ValidationError):
        auth.confirm_reset(raw, "123")
    assert not ResetToken.objects.get().used


def test_UT_PWR_05_no_enumeration(users):
    assert auth.request_reset("unknown@example.test") == auth.request_reset(users["student"].email)
    assert len(mail.outbox) == 1


@pytest.mark.parametrize("status", ["P", "A", "OD"])
def test_UT_ATT_03_mark_status_and_initial_audit(world, status):
    record = mark(world, status)
    assert record.status == status and AuditLog.objects.get(record=record).new == status


@pytest.mark.parametrize(
    "records",
    [
        [],
        [{"student_id": -1, "status": "P"}],
        [{"student_id": True, "status": "P"}],
        [{}],
        ["invalid"],
    ],
)
def test_UT_ATT_06_invalid_roster_atomic(world, records):
    with pytest.raises(DomainError):
        att.submit(world["faculty"], world["session"].pk, records)
    assert not AttendanceRecord.objects.exists() and not AuditLog.objects.exists()


def test_UT_ATT_05_invalid_status(world):
    with pytest.raises(DomainError):
        att.submit(
            world["faculty"],
            world["session"].pk,
            [{"student_id": world["student"].pk, "status": "X"}],
        )
    world["session"].refresh_from_db()
    assert not world["session"].submitted


def test_UT_ATT_04_duplicate_guard(world):
    mark(world)
    with pytest.raises(DomainError) as e:
        mark(world)
    assert e.value.status_code == 409 and AttendanceRecord.objects.count() == 1


def test_duplicate_student_rejected(world):
    rows = [{"student_id": world["student"].pk, "status": "P"}] * 2
    with pytest.raises(DomainError):
        att.submit(world["faculty"], world["session"].pk, rows)


def test_future_session_rejected(world):
    world["session"].date += timedelta(days=1)
    world["session"].save()
    with pytest.raises(DomainError):
        mark(world)


def test_UT_ATT_07_edit_audited(world):
    r = mark(world)
    att.edit(world["faculty"], r.pk, "OD", "Confirmed event")
    log = AuditLog.objects.last()
    assert log.old == "A" and log.new == "OD" and log.editor == world["faculty"]


@pytest.mark.parametrize("status,reason", [("X", "Reason"), ("P", ""), ("P", "  ")])
def test_edit_validation(world, status, reason):
    r = mark(world)
    with pytest.raises(DomainError):
        att.edit(world["faculty"], r.pk, status, reason)
    r.refresh_from_db()
    assert r.status == "A"


def test_other_faculty_cannot_mark_or_edit(world):
    other = User.objects.create_user(username="other", role="FACULTY")
    with pytest.raises(DomainError):
        att.submit(other, world["session"].pk, [])
    r = mark(world)
    with pytest.raises(DomainError):
        att.edit(other, r.pk, "P", "Changed")


def test_UT_COR_01_request_notifies_faculty(world):
    r = mark(world)
    item = att.create_request(world["student"], r.pk, "P", "I was present")
    assert item.state == "PENDING" and Notification.objects.get().user == world["faculty"]


def test_UT_COR_02_own_records_only(world):
    r = mark(world)
    other = User.objects.create_user(username="other", role="STUDENT")
    with pytest.raises(DomainError):
        att.create_request(other, r.pk, "P", "Reason")


@pytest.mark.parametrize("status,reason", [("X", "Reason"), ("P", " "), ("P", None)])
def test_UT_COR_03_validation(world, status, reason):
    r = mark(world)
    with pytest.raises(DomainError):
        att.create_request(world["student"], r.pk, status, reason)


def test_one_open_correction(world):
    r = mark(world)
    att.create_request(world["student"], r.pk, "P", "Reason")
    with pytest.raises(DomainError) as e:
        att.create_request(world["student"], r.pk, "P", "Reason again")
    assert e.value.status_code == 409


@pytest.mark.parametrize(
    "decision,expected,status", [("APPROVE", "APPROVED", "OD"), ("REJECT", "REJECTED", "A")]
)
def test_UT_COR_04_and_05_decision(world, decision, expected, status):
    r = mark(world)
    item = att.create_request(world["student"], r.pk, "OD", "Event")
    att.decide(world["faculty"], item.pk, decision, "Reviewed")
    r.refresh_from_db()
    item.refresh_from_db()
    assert (
        r.status == status
        and item.state == expected
        and Notification.objects.filter(user=world["student"]).exists()
    )


def test_UT_COR_06_repeat_and_invalid(world):
    r = mark(world)
    item = att.create_request(world["student"], r.pk, "P", "Reason")
    with pytest.raises(DomainError):
        att.decide(world["faculty"], item.pk, "UNKNOWN")
    att.decide(world["faculty"], item.pk, "REJECT")
    with pytest.raises(DomainError):
        att.decide(world["faculty"], item.pk, "APPROVE")


@pytest.mark.parametrize("status,percentage", [("P", 100), ("A", 0), ("OD", 100)])
def test_UT_VIEW_01_and_02_percentage(world, status, percentage):
    mark(world, status)
    row = attendance_report(world["student"])[0]
    assert row["percentage"] == percentage


def test_UT_VIEW_03_zero_sessions(world):
    row = attendance_report(world["student"])[0]
    assert row["percentage"] is None and not row["below_threshold"]


def test_UT_VIEW_04_privacy(world):
    other = User.objects.create_user(username="other", role="STUDENT")
    mark(world)
    Enrollment.objects.create(student=other, section=world["section"])
    assert {r["student_id"] for r in attendance_report(world["student"])} == {world["student"].pk}


@pytest.mark.parametrize("value", [0, 75, 100, "74.99"])
def test_UT_ADM_02_threshold_valid(value):
    assert float(threshold_value(value)) == float(value)


@pytest.mark.parametrize("value", [-1, 101, "NaN", "Infinity", "bad", ""])
def test_threshold_invalid(value):
    with pytest.raises(DomainError):
        threshold_value(value)


@pytest.mark.parametrize("threshold,expected", [(0, False), (100, True), (75, True)])
def test_UT_REP_01_strict_threshold(world, threshold, expected):
    mark(world, "A")
    assert (
        attendance_report(world["student"], {"threshold": threshold})[0]["below_threshold"]
        == expected
    )


def test_threshold_equality(world):
    mark(world, "P")
    assert not attendance_report(world["student"], {"threshold": 100})[0]["below_threshold"]


def test_UT_REP_04_date_inclusive(world):
    mark(world)
    day = str(world["session"].date)
    assert attendance_report(world["admin"], {"from": day, "to": day})[0]["held"] == 1
    assert (
        attendance_report(world["admin"], {"from": str(world["session"].date + timedelta(days=1))})[
            0
        ]["held"]
        == 0
    )


@pytest.mark.parametrize(
    "params", [{"from": "bad"}, {"to": "bad"}, {"from": "2026-10-29", "to": "2026-01-01"}]
)
def test_report_bad_dates(world, params):
    with pytest.raises(DomainError):
        attendance_report(world["admin"], params)


def test_UT_REP_03_filters_and_scoping(world):
    mark(world)
    other = User.objects.create_user(username="other", role="FACULTY")
    assert attendance_report(other) == []
    assert (
        len(
            attendance_report(
                world["admin"], {"course": "CS341", "section": "F", "student": "student"}
            )
        )
        == 1
    )
    assert attendance_report(world["admin"], {"course": "NO"}) == []


@pytest.mark.parametrize("fmt,mime", [("csv", "text/csv"), ("pdf", "application/pdf")])
def test_UT_REP_05_and_06_exports(world, fmt, mime):
    mark(world)
    response = export_report(attendance_report(world["admin"]), fmt)
    assert response["Content-Type"] == mime
    assert (
        response.content.startswith(b"%PDF")
        if fmt == "pdf"
        else b"srn,name,course" in response.content
    )


def test_csv_formula_injection(world):
    world["student"].first_name = "=1+1"
    world["student"].save()
    mark(world)
    assert b"'=1+1" in export_report(attendance_report(world["admin"]), "csv").content


def test_invalid_export():
    with pytest.raises(DomainError):
        export_report([], "exe")


def test_pdf_pagination():
    rows = [dict(srn="STU", course="CS", section="F", held=0, attended=0, percentage=None)] * 80
    assert export_report(rows, "pdf").content.startswith(b"%PDF")


def test_UT_CRS_01_unique_code(world):
    with pytest.raises(IntegrityError), transaction.atomic():
        Course.objects.create(code="CS341", title="Duplicate")


@pytest.mark.parametrize(
    "weekday,start,end",
    [(-1, "10:00", "11:00"), (7, "10:00", "11:00"), (0, "11:00", "10:00"), (0, "bad", "11:00")],
)
def test_UT_CRS_02_invalid_slot(world, weekday, start, end):
    with pytest.raises(DomainError):
        courses.create_slot(world["section"], weekday, start, end)


def test_UT_CRS_03_clashes(world):
    with pytest.raises(DomainError):
        courses.create_slot(world["section"], world["slot"].weekday, "09:30", "10:30")
    other = Section.objects.create(course=world["course"], name="E", faculty=world["faculty"])
    with pytest.raises(DomainError):
        courses.create_slot(other, world["slot"].weekday, "09:30", "10:30")


def test_UT_CRS_04_adjacent_valid(world):
    assert courses.create_slot(world["section"], world["slot"].weekday, "10:00", "11:00").pk


def test_invalid_section_faculty(world):
    world["section"].faculty = world["student"]
    world["section"].save()
    with pytest.raises(DomainError):
        courses.create_slot(world["section"], 0, "10:00", "11:00")


def test_UT_CRS_05_csv_partial_success(world):
    other = User.objects.create_user(username="new", role="STUDENT")
    result = courses.bulk_enroll(world["section"], "institute_id\nnew\nunknown\nfaculty\nnew\n")
    assert (
        result["enrolled"] == 1
        and len(result["errors"]) == 2
        and Enrollment.objects.filter(student=other).exists()
    )


def test_csv_invalid_header(world):
    with pytest.raises(DomainError):
        courses.bulk_enroll(world["section"], "wrong\nstudent")


def test_UT_ATT_01_and_02_timetable_and_roster(world):
    assert list(courses.slots_for(world["faculty"])) == [world["session"]]
    assert list(courses.roster(world["section"])) == [world["student"]]
    assert not courses.slots_for(world["faculty"], timezone.localdate() + timedelta(days=1))


@pytest.mark.parametrize("operation", ["save", "delete", "update", "bulk_update", "query_delete"])
def test_UT_ADM_03_and_04_audit_immutable(world, operation):
    mark(world)
    item = AuditLog.objects.first()
    with pytest.raises(ValueError):
        if operation == "save":
            item.reason = "changed"
            item.save()
        elif operation == "delete":
            item.delete()
        elif operation == "update":
            AuditLog.objects.update(reason="changed")
        elif operation == "bulk_update":
            AuditLog.objects.bulk_update([item], ["reason"])
        else:
            AuditLog.objects.all().delete()


def test_UT_NOT_01_and_02_daily_dedup(world):
    mark(world, "A")
    nightly_scan()
    nightly_scan()
    assert Notification.objects.count() == 1


def test_no_low_alert_for_good_attendance(world):
    mark(world, "P")
    nightly_scan()
    assert not Notification.objects.exists()


def test_email_after_commit_and_idempotent(world, django_capture_on_commit_callbacks):
    with django_capture_on_commit_callbacks(execute=True):
        item = notify(world["student"], "Hello", "test-key")
    item.refresh_from_db()
    assert item.email_sent and len(mail.outbox) == 1
    deliver_email(item.pk)
    assert len(mail.outbox) == 1


def test_UT_NOT_03_email_failure_deadletter(world):
    item = Notification.objects.create(user=world["student"], message="hello", key="failed")
    with patch("notifications.tasks.send_mail", side_effect=OSError("offline")):
        deliver_email.apply(args=[item.pk], throw=False)
    item.refresh_from_db()
    assert not item.email_sent and item.email_error == "OSError" and item.email_attempts >= 1


@pytest.mark.parametrize(
    "statement", ["UPDATE audit_auditlog SET reason='tampered'", "DELETE FROM audit_auditlog"]
)
def test_raw_sql_cannot_change_audit(world, statement):
    from django.db import connection, DatabaseError

    mark(world)
    with pytest.raises(DatabaseError), transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(statement)
    assert AuditLog.objects.count() == 1
