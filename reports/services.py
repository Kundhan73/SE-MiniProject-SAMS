import csv
import io
from decimal import Decimal, InvalidOperation
from datetime import date
from django.db.models import Count, Q
from django.http import HttpResponse
from courses.models import Enrollment
from attendance.models import AttendanceRecord, SystemConfig
from core.errors import DomainError


def threshold_value(raw=None):
    try:
        value = (
            Decimal(str(raw))
            if raw is not None
            else Decimal(str(SystemConfig.objects.get_or_create(pk=1)[0].threshold))
        )
    except (InvalidOperation, ValueError, TypeError):
        raise DomainError("INVALID_THRESHOLD", "Threshold must be a number from 0 to 100.")
    if not value.is_finite() or not 0 <= value <= 100:
        raise DomainError("INVALID_THRESHOLD", "Threshold must be a number from 0 to 100.")
    return value


def attendance_report(user, params=None):
    params = params or {}
    threshold = threshold_value(params.get("threshold"))
    enrollments = Enrollment.objects.select_related("student", "section__course")
    if user.role == "STUDENT":
        enrollments = enrollments.filter(student=user)
    elif user.role == "FACULTY":
        enrollments = enrollments.filter(section__faculty=user)
    for key, field in [
        ("course", "section__course__code"),
        ("section", "section__name"),
        ("student", "student__username"),
    ]:
        if params.get(key):
            enrollments = enrollments.filter(**{field: params[key]})
    records = AttendanceRecord.objects.filter(session__submitted=True)
    for key, lookup in [("from", "session__date__gte"), ("to", "session__date__lte")]:
        if params.get(key):
            try:
                day = date.fromisoformat(params[key])
            except (ValueError, TypeError):
                raise DomainError("INVALID_DATE", "Use dates in YYYY-MM-DD format.")
            records = records.filter(**{lookup: day})
    if params.get("from") and params.get("to") and params["from"] > params["to"]:
        raise DomainError("INVALID_DATE_RANGE", "Start date must not follow end date.")
    if user.role == "STUDENT":
        records = records.filter(student=user)
    elif user.role == "FACULTY":
        records = records.filter(session__faculty=user)
    counts = {
        (r["student_id"], r["session__section_id"]): r
        for r in records.values("student_id", "session__section_id").annotate(
            held=Count("id"), attended=Count("id", filter=Q(status__in=["P", "OD"]))
        )
    }
    result = []
    for e in enrollments.order_by("student__username", "section__course__code"):
        count = counts.get((e.student_id, e.section_id), {"held": 0, "attended": 0})
        percent = Decimal(count["attended"]) * 100 / count["held"] if count["held"] else None
        result.append(
            {
                "student_id": e.student_id,
                "srn": e.student.username,
                "name": e.student.get_full_name() or e.student.username,
                "section_id": e.section_id,
                "section": e.section.name,
                "course": e.section.course.code,
                "held": count["held"],
                "attended": count["attended"],
                "percentage": round(float(percent), 2) if percent is not None else None,
                "below_threshold": percent is not None and percent < threshold,
            }
        )
    return result


def export_report(rows, output):
    fields = ["srn", "name", "course", "section", "held", "attended", "percentage"]
    if output == "csv":
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(fields)
        for row in rows:
            # Neutralize formulas when opening exports in a spreadsheet.
            writer.writerow(
                [
                    ("'" + str(row[f]))
                    if str(row[f]).startswith(("=", "+", "-", "@", "\t", "\r"))
                    else row[f]
                    for f in fields
                ]
            )
        response = HttpResponse(buffer.getvalue(), content_type="text/csv")
    elif output == "pdf":
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import landscape, A4

        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=landscape(A4))
        pdf.setTitle("SAMS Attendance Report")
        y = 555
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(40, y, "SAMS | Attendance report")
        y -= 32
        for row in rows:
            if y < 45:
                pdf.showPage()
                y = 555
            pdf.setFont("Helvetica", 10)
            percentage = f"{row['percentage']}%" if row["percentage"] is not None else "No classes"
            text = f"{row['srn']} | {row['course']} / {row['section']} | {row['attended']}/{row['held']} | {percentage}"
            pdf.drawString(40, y, text[:140])
            y -= 20
        pdf.save()
        response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    else:
        raise DomainError("INVALID_FORMAT", "Choose json, csv or pdf.")
    response["Content-Disposition"] = f'attachment; filename="sams-attendance.{output}"'
    return response
