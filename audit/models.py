from django.db import models
from django.conf import settings


class AppendOnlyQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValueError("Audit entries are append-only")

    def delete(self):
        raise ValueError("Audit entries are append-only")

    def bulk_update(self, *args, **kwargs):
        raise ValueError("Audit entries are append-only")


class AuditLog(models.Model):
    record = models.ForeignKey("attendance.AttendanceRecord", on_delete=models.PROTECT)
    editor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    old = models.CharField(max_length=2, blank=True)
    new = models.CharField(max_length=2)
    reason = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    objects = AppendOnlyQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValueError("Audit entries are append-only")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Audit entries are append-only")
