import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from courses.models import Course, Section, Enrollment, TimetableSlot
from attendance.models import ClassSession
from datetime import time


@pytest.fixture(autouse=True)
def test_settings(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


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


@pytest.fixture
def world(users):
    c = Course.objects.create(code="CS341", title="Software Engineering")
    section = Section.objects.create(course=c, name="F", faculty=users["faculty"])
    Enrollment.objects.create(section=section, student=users["student"])
    slot = TimetableSlot.objects.create(
        section=section, weekday=timezone.localdate().weekday(), start=time(9), end=time(10)
    )
    session = ClassSession.objects.create(
        section=section, slot=slot, date=timezone.localdate(), faculty=users["faculty"]
    )
    return {**users, "course": c, "section": section, "slot": slot, "session": session}
