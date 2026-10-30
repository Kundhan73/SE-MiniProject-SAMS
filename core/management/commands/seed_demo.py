import os
from datetime import timedelta, time
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from accounts.models import User
from courses.models import Course, Section, Enrollment, TimetableSlot
from attendance.models import ClassSession, AttendanceRecord
from audit.models import AuditLog


class Command(BaseCommand):
    help = "Create synthetic demo accounts, timetable and six weeks of attendance; never overwrites existing data."

    def add_arguments(self, parser):
        parser.add_argument("--full", action="store_true", help="2,000 students and 100 faculty")

    @transaction.atomic
    def handle(self, *args, **options):
        if User.objects.exists():
            raise CommandError("Database is not empty. Seed only a new demo database.")
        password = os.getenv("DEMO_PASSWORD", "DemoPass@1234")
        admin = User.objects.create_user(
            username="ADM001",
            password=password,
            email="admin@example.test",
            first_name="Demo administrator",
            role="ADMIN",
        )
        faculties = [
            User.objects.create_user(
                username=f"FAC{i + 1:03}",
                password=password,
                email=f"faculty{i + 1}@example.test",
                first_name=f"Faculty {i + 1}",
                role="FACULTY",
            )
            for i in range(100 if options["full"] else 2)
        ]
        # Hash once; synthetic accounts share the explicitly documented demo password.
        hashed = admin.password
        students = User.objects.bulk_create(
            [
                User(
                    username=f"STU{i + 1:03}",
                    password=hashed,
                    email=f"student{i + 1}@example.test",
                    first_name=f"Student {i + 1:03}",
                    role="STUDENT",
                )
                for i in range(2000 if options["full"] else 60)
            ]
        )
        day = timezone.localdate()
        titles = ["Software Engineering", "Database Management Systems", "Machine Learning"]
        for index in range(20 if options["full"] else 3):
            course = Course.objects.create(
                code=f"CS{341 + index}", title=titles[index] if index < 3 else f"Course {index + 1}"
            )
            section = Section.objects.create(
                course=course, name="F", faculty=faculties[index % len(faculties)]
            )
            selected = students[index * 100 : (index + 1) * 100] if options["full"] else students
            Enrollment.objects.bulk_create(
                [Enrollment(section=section, student=s) for s in selected]
            )
            # Different time slots avoid faculty clashes even when a faculty teaches several courses.
            slot = TimetableSlot.objects.create(
                section=section,
                weekday=day.weekday(),
                start=time(9 + index % 8),
                end=time(10 + index % 8),
            )
            for week in range(1, 7):
                session = ClassSession.objects.create(
                    section=section,
                    slot=slot,
                    date=day - timedelta(weeks=week),
                    faculty=section.faculty,
                    submitted=True,
                )
                records = AttendanceRecord.objects.bulk_create(
                    [
                        AttendanceRecord(
                            session=session,
                            student=s,
                            status="A"
                            if (j + week + index) % 3 == 0
                            else ("OD" if (j + week) % 7 == 0 else "P"),
                        )
                        for j, s in enumerate(selected)
                    ]
                )
                AuditLog.objects.bulk_create(
                    [
                        AuditLog(
                            record=r,
                            editor=section.faculty,
                            old="",
                            new=r.status,
                            reason="Synthetic demo history",
                        )
                        for r in records
                    ]
                )
            ClassSession.objects.create(
                section=section, slot=slot, date=day, faculty=section.faculty
            )
        self.stdout.write(
            self.style.SUCCESS(
                f"Synthetic demo ready: {len(students)} students, {len(faculties)} faculty. Accounts ADM001, FAC001, STU001."
            )
        )
