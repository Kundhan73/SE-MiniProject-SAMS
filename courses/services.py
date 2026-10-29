import csv
import io
from datetime import datetime
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from accounts.models import User
from core.errors import DomainError
from .models import Enrollment, TimetableSlot, Section


@transaction.atomic
def create_slot(section, weekday, start, end):
    # Lock all sections assigned to this faculty to serialize overlapping timetable changes.
    list(Section.objects.select_for_update().filter(faculty=section.faculty).order_by("pk"))
    try:
        weekday = int(weekday)
        start = datetime.strptime(start, "%H:%M").time()
        end = datetime.strptime(end, "%H:%M").time()
    except (ValueError, TypeError):
        raise DomainError("INVALID_SLOT", "Use weekday 0–6 and HH:MM times.")
    if not 0 <= weekday <= 6 or end <= start:
        raise DomainError("INVALID_SLOT", "End must follow start; weekday must be 0–6.")
    if section.faculty.role != "FACULTY":
        raise DomainError("INVALID_FACULTY", "Assign a faculty account to the section.")
    if (
        TimetableSlot.objects.filter(weekday=weekday, start__lt=end, end__gt=start)
        .filter(Q(section=section) | Q(section__faculty=section.faculty))
        .exists()
    ):
        raise DomainError(
            "TIMETABLE_CLASH", "Faculty or section already has a class at this time.", 409
        )
    return TimetableSlot.objects.create(section=section, weekday=weekday, start=start, end=end)


def roster(section):
    return User.objects.filter(enrollment__section=section).order_by("username")


def slots_for(faculty, day=None):
    from attendance.models import ClassSession

    day = day or timezone.localdate()
    for slot in TimetableSlot.objects.filter(
        section__faculty=faculty, weekday=day.weekday()
    ).select_related("section"):
        ClassSession.objects.get_or_create(
            slot=slot, date=day, defaults={"section": slot.section, "faculty": faculty}
        )
    return (
        ClassSession.objects.filter(faculty=faculty, date=day)
        .select_related("section__course", "slot")
        .order_by("slot__start")
    )


def bulk_enroll(section, content):
    reader = csv.DictReader(io.StringIO(content))
    if not reader.fieldnames or "institute_id" not in reader.fieldnames:
        raise DomainError("INVALID_CSV", "CSV needs an institute_id header.")
    result = {"enrolled": 0, "errors": []}
    for number, row in enumerate(reader, 2):
        user = User.objects.filter(
            username=row.get("institute_id"), role="STUDENT", is_active=True
        ).first()
        if not user:
            result["errors"].append({"row": number, "reason": "Unknown or inactive student"})
            continue
        _, created = Enrollment.objects.get_or_create(section=section, student=user)
        result["enrolled"] += int(created)
    return result
