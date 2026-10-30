from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.db import transaction
from .models import Notification


@shared_task(autoretry_for=(OSError,), retry_backoff=True, max_retries=3)
def send_reset(email, link):
    send_mail("Reset your SAMS password", f"Use this link within 30 minutes: {link}", None, [email])


@shared_task(bind=True, max_retries=3)
def deliver_email(self, notification_id):
    item = Notification.objects.select_related("user").get(pk=notification_id)
    if item.email_sent:
        return
    try:
        send_mail("SAMS attendance update", item.message, None, [item.user.email])
        item.email_sent = True
        item.email_error = ""
    except Exception as exc:
        item.email_attempts += 1
        item.email_error = type(exc).__name__
        item.save()
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=2**self.request.retries)
        return
    item.save()


def notify(user, message, key):
    item, created = Notification.objects.get_or_create(
        key=key, defaults={"user": user, "message": message}
    )
    if created:
        transaction.on_commit(lambda: deliver_email.delay(item.pk))
    return item


@shared_task
def nightly_scan():
    from accounts.models import User
    from reports.services import attendance_report

    for user in User.objects.filter(role="STUDENT", is_active=True):
        for row in attendance_report(user):
            if row["below_threshold"]:
                notify(
                    user,
                    f"Attendance in {row['course']}: {row['percentage']}%, below the minimum.",
                    f"low:{user.pk}:{row['section_id']}:{timezone.localdate()}",
                )
