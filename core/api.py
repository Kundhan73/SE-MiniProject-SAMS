from functools import wraps
from drf_spectacular.utils import extend_schema, OpenApiResponse
from core.schema import REQUESTS, ERROR
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection, transaction
from django.conf import settings
from django.contrib.auth import login as django_login, logout as django_logout
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from datetime import timedelta
from accounts.models import User, LoginSession
from accounts import services as auth
from attendance.models import AttendanceRecord, CorrectionRequest, SystemConfig
from attendance import services as att
from courses.models import Course, Section, TimetableSlot, Enrollment
from courses import services as courses
from notifications.models import Notification
from audit.models import AuditLog
from reports.services import attendance_report, export_report, threshold_value
from core.errors import DomainError
from core.permissions import require_role


def endpoint(methods, public=False, roles=()):
    def decorate(fn):
        @wraps(fn)
        def handler(request, *args, **kwargs):
            if roles:
                require_role(request.user, *roles)
            try:
                if fn.__name__ == "login":
                    from rest_framework.authentication import SessionAuthentication

                    SessionAuthentication().enforce_csrf(request)
                return fn(request, *args, **kwargs)
            except ObjectDoesNotExist:
                raise DomainError("NOT_FOUND", "The requested record does not exist.", 404)
            except (ValueError, TypeError) as exc:
                raise DomainError("INVALID_INPUT", "Check the values supplied.") from exc

        handler = permission_classes([AllowAny])(handler) if public else handler
        view = api_view(methods)(handler)
        return extend_schema(
            request={"application/json": REQUESTS[fn.__name__]}
            if fn.__name__ in REQUESTS
            else None,
            responses={
                200: OpenApiResponse(
                    description="Successful response; see docs/API.md for the resource shape."
                ),
                201: OpenApiResponse(description="Created"),
                400: ERROR,
                401: ERROR,
                403: ERROR,
                409: ERROR,
            },
            description=f"Allowed roles: {', '.join(roles) if roles else ('Public' if public else 'Any authenticated role')}. Errors use the standard error envelope.",
            tags=[fn.__name__.split("_")[0]],
        )(view)

    return decorate


def input_data(request, **fields):
    serializer = type("Input", (serializers.Serializer,), fields)(data=request.data)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


def user_data(user):
    return {
        "id": user.pk,
        "institute_id": user.username,
        "name": user.get_full_name() or user.username,
        "role": user.role,
        "email": user.email,
        "is_active": user.is_active,
    }


@endpoint(["GET"], public=True)
def health(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()
    if not settings.CELERY_TASK_ALWAYS_EAGER:
        import redis

        try:
            redis.Redis.from_url(settings.CELERY_BROKER_URL, socket_connect_timeout=2).ping()
        except redis.RedisError:
            return Response({"status": "unavailable"}, status=503)
    return Response({"status": "ok"})


@endpoint(["POST"], public=True)
def login(request):
    data = input_data(
        request,
        institute_id=serializers.CharField(max_length=150),
        password=serializers.CharField(max_length=256),
    )
    user, tokens = auth.authenticate(**data)
    django_login(request._request, user, backend="django.contrib.auth.backends.ModelBackend")
    request.session["jwt_session_id"] = RefreshToken(tokens["refresh"])["sid"]
    return Response({**tokens, "user": user_data(user)})


@endpoint(["POST"])
def logout(request):
    ids = {request.session.get("jwt_session_id")}
    if request.auth:
        ids.add(request.auth.get("sid"))
    LoginSession.objects.filter(pk__in=[sid for sid in ids if sid], user=request.user).update(
        active=False
    )
    django_logout(request._request)
    return Response(status=205)


@endpoint(["POST"], public=True)
def refresh(request):
    data = input_data(request, refresh=serializers.CharField())
    try:
        token = RefreshToken(data["refresh"])
        item = (
            LoginSession.objects.select_related("user")
            .filter(pk=token.get("sid"), active=True)
            .first()
        )
        if (
            not item
            or not item.user.is_active
            or item.last_seen + timedelta(seconds=settings.SESSION_COOKIE_AGE) <= timezone.now()
        ):
            raise DomainError("SESSION_EXPIRED", "Sign in again.", 401)
        item.last_seen = timezone.now()
        item.save(update_fields=["last_seen"])
        return Response({"access": str(token.access_token)})
    except TokenError:
        raise DomainError("TOKEN_INVALID", "Token is invalid or expired.", 401)


@endpoint(["POST"], public=True)
def password_reset(request):
    data = input_data(request, email=serializers.EmailField())
    return Response(auth.request_reset(data["email"]), status=202)


@endpoint(["POST"], public=True)
def password_confirm(request):
    data = input_data(
        request, token=serializers.CharField(), new_password=serializers.CharField(max_length=256)
    )
    auth.confirm_reset(**data)
    return Response({"message": "Password updated. Sign in again."})


@endpoint(["GET"])
def me(request):
    return Response(user_data(request.user))


@endpoint(["GET"], roles=("FACULTY",))
def today(request):
    result = []
    for session in courses.slots_for(request.user):
        marks = {r.student_id: r for r in session.records.select_related("student")}
        students = (
            [r.student for r in marks.values()]
            if session.submitted
            else courses.roster(session.section)
        )
        result.append(
            {
                "session_id": session.pk,
                "course": session.section.course.code,
                "section": session.section.name,
                "date": str(session.date),
                "start": str(session.slot.start),
                "submitted": session.submitted,
                "roster": [
                    {
                        "student_id": s.pk,
                        "srn": s.username,
                        "name": s.get_full_name() or s.username,
                        "status": marks[s.pk].status if s.pk in marks else "P",
                        "record_id": marks[s.pk].pk if s.pk in marks else None,
                    }
                    for s in students
                ],
            }
        )
    return Response(result)


@endpoint(["POST"], roles=("FACULTY",))
def submit(request, session_id):
    data = input_data(
        request, records=serializers.ListField(child=serializers.DictField(), allow_empty=False)
    )
    return Response(att.submit(request.user, session_id, data["records"]), status=201)


@endpoint(["PATCH"], roles=("FACULTY", "ADMIN"))
def record_edit(request, record_id):
    data = input_data(
        request,
        status=serializers.ChoiceField(choices=["P", "A", "OD"]),
        reason=serializers.CharField(max_length=1000),
    )
    item = att.edit(request.user, record_id, **data)
    return Response({"id": item.pk, "status": item.status})


@endpoint(["GET"], roles=("STUDENT",))
def student_attendance(request):
    return Response(attendance_report(request.user, request.query_params))


@endpoint(["GET"], roles=("STUDENT",))
def student_records(request):
    rows = (
        AttendanceRecord.objects.filter(student=request.user)
        .select_related("session__section__course")
        .order_by("-session__date", "-pk")[:500]
    )
    return Response(
        [
            {
                "id": r.pk,
                "date": str(r.session.date),
                "course": r.session.section.course.code,
                "status": r.status,
            }
            for r in rows
        ]
    )


@endpoint(["GET", "POST"])
def corrections(request):
    if request.method == "POST":
        data = input_data(
            request,
            record_id=serializers.IntegerField(min_value=1),
            requested_status=serializers.ChoiceField(choices=["P", "A", "OD"]),
            reason=serializers.CharField(max_length=1000),
        )
        item = att.create_request(
            request.user, data["record_id"], data["requested_status"], data["reason"]
        )
        return Response({"id": item.pk, "state": item.state}, status=201)
    rows = CorrectionRequest.objects.select_related(
        "record__student", "record__session__section__course"
    )
    if request.user.role == "STUDENT":
        rows = rows.filter(record__student=request.user)
    elif request.user.role == "FACULTY":
        rows = rows.filter(record__session__faculty=request.user)
    return Response(
        [
            {
                "id": r.pk,
                "record_id": r.record_id,
                "student": r.record.student.username,
                "course": r.record.session.section.course.code,
                "date": str(r.record.session.date),
                "status": r.record.status,
                "requested_status": r.requested_status,
                "reason": r.reason,
                "state": r.state,
                "note": r.note,
            }
            for r in rows.order_by("-pk")[:500]
        ]
    )


@endpoint(["PATCH"], roles=("FACULTY",))
def correction_decide(request, request_id):
    data = input_data(
        request,
        decision=serializers.ChoiceField(choices=["APPROVE", "REJECT"]),
        note=serializers.CharField(required=False, allow_blank=True, max_length=1000),
    )
    item = att.decide(request.user, request_id, **data)
    return Response({"id": item.pk, "state": item.state})


@endpoint(["GET"], roles=("FACULTY", "ADMIN"))
def report(request, kind="summary"):
    # DRF reserves ?format= for renderer selection; exports use ?export= at the router.
    rows = attendance_report(request.user, request.query_params)
    if kind == "defaulters":
        rows = [r for r in rows if r["below_threshold"]]
    output = request.query_params.get("export", request.query_params.get("format", "json"))
    return export_report(rows, output) if output != "json" else Response(rows)


@endpoint(["GET", "POST"], roles=("ADMIN",))
@transaction.atomic
def course_list(request):
    if request.method == "POST":
        data = input_data(
            request,
            code=serializers.CharField(max_length=30),
            title=serializers.CharField(max_length=160),
        )
        item = Course.objects.create(**data)
        return Response({"id": item.pk, **data}, status=201)
    return Response(list(Course.objects.values("id", "code", "title").order_by("code")))


@endpoint(["GET", "POST"], roles=("ADMIN",))
@transaction.atomic
def sections(request):
    if request.method == "POST":
        data = input_data(
            request,
            course_id=serializers.IntegerField(min_value=1),
            faculty_id=serializers.IntegerField(min_value=1),
            name=serializers.CharField(max_length=30),
        )
        User.objects.get(pk=data["faculty_id"], role="FACULTY", is_active=True)
        Course.objects.get(pk=data["course_id"])
        item = Section.objects.create(**data)
        return Response({"id": item.pk, **data}, status=201)
    return Response(
        list(
            Section.objects.values(
                "id", "name", "course_id", "course__code", "faculty_id", "faculty__username"
            ).order_by("course__code", "name")
        )
    )


@endpoint(["GET", "POST"], roles=("ADMIN",))
def timetable(request):
    if request.method == "POST":
        data = input_data(
            request,
            section_id=serializers.IntegerField(min_value=1),
            weekday=serializers.IntegerField(min_value=0, max_value=6),
            start=serializers.CharField(),
            end=serializers.CharField(),
        )
        section = Section.objects.get(pk=data.pop("section_id"))
        item = courses.create_slot(section, **data)
        return Response({"id": item.pk}, status=201)
    return Response(
        list(
            TimetableSlot.objects.values(
                "id", "section_id", "section__course__code", "weekday", "start", "end"
            )
        )
    )


@endpoint(["POST"], roles=("ADMIN",))
def enroll(request, section_id):
    section = Section.objects.get(pk=section_id)
    data = input_data(request, csv=serializers.CharField(max_length=500000))
    return Response(courses.bulk_enroll(section, data["csv"]))


@endpoint(["GET", "POST"], roles=("ADMIN",))
@transaction.atomic
def users(request):
    if request.method == "POST":
        data = input_data(
            request,
            institute_id=serializers.CharField(max_length=150),
            email=serializers.EmailField(),
            name=serializers.CharField(max_length=150),
            password=serializers.CharField(max_length=256),
            role=serializers.ChoiceField(choices=["STUDENT", "FACULTY", "ADMIN"]),
        )
        from django.contrib.auth.password_validation import validate_password

        validate_password(data["password"])
        if User.objects.filter(email__iexact=data["email"]).exists():
            raise DomainError("DUPLICATE_EMAIL", "An account already uses this email.", 409)
        user = User.objects.create_user(
            username=data["institute_id"],
            email=data["email"],
            first_name=data["name"],
            password=data["password"],
            role=data["role"],
        )
        return Response(user_data(user), status=201)
    rows = User.objects.all().order_by("username")
    if request.query_params.get("q"):
        rows = rows.filter(username__icontains=request.query_params["q"])
    return Response([user_data(u) for u in rows[:2500]])


@endpoint(["PATCH"], roles=("ADMIN",))
def user_edit(request, user_id):
    user = User.objects.get(pk=user_id)
    data = input_data(
        request,
        role=serializers.ChoiceField(choices=["STUDENT", "FACULTY", "ADMIN"], required=False),
        is_active=serializers.BooleanField(required=False),
    )
    if user == request.user and (
        data.get("is_active") is False or data.get("role", user.role) != "ADMIN"
    ):
        raise DomainError("SELF_LOCKOUT", "You cannot remove your own administrator access.")
    if (
        "role" in data
        and data["role"] != user.role
        and (
            Section.objects.filter(faculty=user).exists()
            or Enrollment.objects.filter(student=user).exists()
        )
    ):
        raise DomainError(
            "ROLE_IN_USE", "Remove active course assignments before changing this role.", 409
        )
    for key, value in data.items():
        setattr(user, key, value)
    user.save()
    LoginSession.objects.filter(user=user).update(active=False)
    return Response(user_data(user))


@endpoint(["GET", "PATCH"], roles=("ADMIN",))
def config(request):
    item, _ = SystemConfig.objects.get_or_create(pk=1)
    if request.method == "PATCH":
        data = input_data(
            request,
            threshold=serializers.DecimalField(
                max_digits=5, decimal_places=2, min_value=0, max_value=100
            ),
        )
        item.threshold = threshold_value(data["threshold"])
        item.save()
    return Response({"threshold": float(item.threshold)})


@endpoint(["GET"], roles=("ADMIN",))
def audit(request):
    rows = AuditLog.objects.select_related("editor").order_by("-pk")
    for param, field in [
        ("record", "record_id"),
        ("editor", "editor_id"),
        ("from", "timestamp__date__gte"),
        ("to", "timestamp__date__lte"),
    ]:
        if request.query_params.get(param):
            rows = rows.filter(**{field: request.query_params[param]})
    page = max(1, int(request.query_params.get("page", 1)))
    return Response(
        {
            "count": rows.count(),
            "results": [
                {
                    "id": r.pk,
                    "record_id": r.record_id,
                    "editor": r.editor.username,
                    "old": r.old,
                    "new": r.new,
                    "reason": r.reason,
                    "timestamp": r.timestamp.isoformat(),
                }
                for r in rows[(page - 1) * 100 : page * 100]
            ],
        }
    )


@endpoint(["GET"])
def notifications(request):
    return Response(
        list(
            Notification.objects.filter(user=request.user)
            .order_by("-pk")
            .values("id", "message", "read", "created_at")[:100]
        )
    )


@endpoint(["POST"])
def notification_read(request, notification_id):
    item = Notification.objects.get(pk=notification_id, user=request.user)
    item.read = True
    item.save(update_fields=["read"])
    return Response({"read": True})


@endpoint(["GET"], roles=("ADMIN",))
def email_failures(request):
    return Response(
        list(
            Notification.objects.exclude(email_error="").values(
                "id", "email_attempts", "email_error", "email_sent"
            )
        )
    )
