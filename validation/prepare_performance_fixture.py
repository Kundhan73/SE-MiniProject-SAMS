import os
import sys
import json
from datetime import time

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sams.settings")
import django

django.setup()
from django.utils import timezone
from accounts.models import User
from courses.models import Section, TimetableSlot
from attendance.models import ClassSession, AttendanceRecord

today = timezone.localdate()
for section in Section.objects.select_related("faculty"):
    slot, _ = TimetableSlot.objects.get_or_create(
        section=section, weekday=today.weekday(), start=time(18), end=time(19)
    )
    ClassSession.objects.get_or_create(
        section=section, slot=slot, date=today, defaults={"faculty": section.faculty}
    )
print(
    json.dumps(
        {
            "commit": "05ce0282959ab2084b553bcd1e43aa312961d21c",
            "fixture_date": str(today),
            "students": User.objects.filter(role="STUDENT").count(),
            "faculty": User.objects.filter(role="FACULTY").count(),
            "sections": Section.objects.count(),
            "held_records": AttendanceRecord.objects.count(),
            "pending_today": ClassSession.objects.filter(date=today, submitted=False).count(),
            "origin": "Private snapshot of the existing synthetic seed; session and notification rows excluded; current-day marking fixtures added.",
        },
        indent=2,
    )
)
