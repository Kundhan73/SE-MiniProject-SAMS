from django.db import transaction
from django.utils import timezone
from core.errors import DomainError
from core.permissions import require_role
from courses.services import roster
from audit.models import AuditLog
from notifications.tasks import notify
from .models import ClassSession, AttendanceRecord, CorrectionRequest

VALID_STATUSES = {"P", "A", "OD"}


def can_edit(user, session):
    if user.role != "ADMIN" and (user.role != "FACULTY" or session.faculty_id != user.pk):
        raise DomainError(
            "NOT_SESSION_FACULTY", "This session belongs to another faculty member.", 403
        )


@transaction.atomic
def submit(user, session_id, records):
    require_role(user, "FACULTY")
    session = ClassSession.objects.select_for_update().get(pk=session_id)
    can_edit(user, session)
    if session.date > timezone.localdate():
        raise DomainError("FUTURE_SESSION", "Cannot mark attendance before the class date.")
    if session.submitted:
        raise DomainError(
            "ALREADY_SUBMITTED", "Attendance already submitted. Use an explicit edit.", 409
        )
    if not isinstance(records, list) or not records:
        raise DomainError("INVALID_RECORDS", "Provide the complete roll list.")
    ids = [r.get("student_id") for r in records if isinstance(r, dict)]
    if len(ids) != len(records) or any(not isinstance(i, int) or isinstance(i, bool) for i in ids):
        raise DomainError("INVALID_RECORDS", "Each row needs an integer student_id.")
    if any(r.get("status") not in VALID_STATUSES for r in records):
        raise DomainError("INVALID_STATUS", "Use P, A or OD.")
    expected = set(roster(session.section).values_list("id", flat=True))
    if set(ids) != expected or len(ids) != len(set(ids)):
        raise DomainError("NOT_IN_ROSTER", "Submit each enrolled student exactly once.")
    created = AttendanceRecord.objects.bulk_create(
        [
            AttendanceRecord(session=session, student_id=r["student_id"], status=r["status"])
            for r in records
        ]
    )
    AuditLog.objects.bulk_create(
        [
            AuditLog(record=r, editor=user, old="", new=r.status, reason="Initial submission")
            for r in created
        ]
    )
    session.submitted = True
    session.save(update_fields=["submitted"])
    return {
        "session_id": session.pk,
        "saved": len(created),
        "present": sum(r.status == "P" for r in created),
        "absent": sum(r.status == "A" for r in created),
        "on_duty": sum(r.status == "OD" for r in created),
    }


@transaction.atomic
def edit(user, record_id, status, reason):
    record = (
        AttendanceRecord.objects.select_for_update().select_related("session").get(pk=record_id)
    )
    can_edit(user, record.session)
    if status not in VALID_STATUSES or not isinstance(reason, str) or not reason.strip():
        raise DomainError("INVALID_EDIT", "Select P, A or OD and provide a reason.")
    old = record.status
    record.status = status
    record.save(update_fields=["status"])
    AuditLog.objects.create(record=record, editor=user, old=old, new=status, reason=reason.strip())
    return record


@transaction.atomic
def create_request(user, record_id, status, reason):
    require_role(user, "STUDENT")
    record = (
        AttendanceRecord.objects.select_for_update()
        .select_related("session__faculty")
        .get(pk=record_id)
    )
    if record.student_id != user.pk:
        raise DomainError(
            "NOT_OWN_RECORD", "You may request changes only to your own attendance.", 403
        )
    if status not in VALID_STATUSES or not isinstance(reason, str) or not reason.strip():
        raise DomainError("INVALID_CORRECTION", "A valid status and reason are required.")
    if CorrectionRequest.objects.filter(record=record, state="PENDING").exists():
        raise DomainError("OPEN_REQUEST_EXISTS", "A correction is already pending.", 409)
    item = CorrectionRequest.objects.create(
        record=record, requested_status=status, reason=reason.strip()
    )
    notify(
        record.session.faculty,
        f"{user.username} requested an attendance correction.",
        f"correction:{item.pk}",
    )
    return item


@transaction.atomic
def decide(user, request_id, decision, note=""):
    require_role(user, "FACULTY")
    item = (
        CorrectionRequest.objects.select_for_update()
        .select_related("record__session", "record__student")
        .get(pk=request_id)
    )
    can_edit(user, item.record.session)
    if item.state != "PENDING":
        raise DomainError("ALREADY_DECIDED", "This request has already been reviewed.", 409)
    if decision not in {"APPROVE", "REJECT"}:
        raise DomainError("INVALID_DECISION", "Choose APPROVE or REJECT.")
    if decision == "APPROVE":
        edit(user, item.record_id, item.requested_status, f"Correction approved: {item.reason}")
    item.state = "APPROVED" if decision == "APPROVE" else "REJECTED"
    item.note = str(note)
    item.save(update_fields=["state", "note"])
    notify(
        item.record.student,
        f"Your correction request was {item.state.lower()}.",
        f"decision:{item.pk}",
    )
    return item
