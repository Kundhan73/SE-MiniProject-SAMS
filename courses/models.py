from django.db import models
from django.conf import settings


class Course(models.Model):
    code = models.CharField(max_length=30, unique=True)
    title = models.CharField(max_length=160)


class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    name = models.CharField(max_length=30)
    faculty = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["course", "name"], name="unique_section")]


class Enrollment(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["section", "student"], name="unique_enrollment")
        ]


class TimetableSlot(models.Model):
    section = models.ForeignKey(Section, on_delete=models.PROTECT)
    weekday = models.PositiveSmallIntegerField()
    start = models.TimeField()
    end = models.TimeField()

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(weekday__lte=6), name="valid_weekday"),
            models.CheckConstraint(
                condition=models.Q(end__gt=models.F("start")), name="positive_slot"
            ),
        ]
