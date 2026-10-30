from django.db import models
from django.conf import settings
from courses.models import Section, TimetableSlot

STATUSES = [("P", "Present"), ("A", "Absent"), ("OD", "On Duty")]


class ClassSession(models.Model):
    section = models.ForeignKey(Section, on_delete=models.PROTECT)
    slot = models.ForeignKey(TimetableSlot, on_delete=models.PROTECT)
    date = models.DateField(db_index=True)
    faculty = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    submitted = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["slot", "date"], name="unique_slot_day")]


class AttendanceRecord(models.Model):
    session = models.ForeignKey(ClassSession, on_delete=models.PROTECT, related_name="records")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    status = models.CharField(max_length=2, choices=STATUSES)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["session", "student"], name="unique_mark"),
            models.CheckConstraint(
                condition=models.Q(status__in=["P", "A", "OD"]), name="valid_attendance_status"
            ),
        ]


class CorrectionRequest(models.Model):
    record = models.ForeignKey(AttendanceRecord, on_delete=models.PROTECT)
    requested_status = models.CharField(max_length=2, choices=STATUSES)
    reason = models.TextField()
    state = models.CharField(max_length=10, default="PENDING")
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["record"], condition=models.Q(state="PENDING"), name="one_open_correction"
            )
        ]


class SystemConfig(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True, default=1)
    threshold = models.DecimalField(max_digits=5, decimal_places=2, default=75)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(threshold__gte=0, threshold__lte=100), name="valid_threshold"
            )
        ]
