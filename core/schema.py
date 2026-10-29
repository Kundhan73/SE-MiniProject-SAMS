"""OpenAPI request contracts for the function-based API views."""

from drf_spectacular.extensions import OpenApiAuthenticationExtension


class SessionJWTSpec(OpenApiAuthenticationExtension):
    target_class = "accounts.authentication.IdleJWTAuthentication"
    name = "bearerAuth"

    def get_security_definition(self, auto_schema):
        return {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}


def obj(**properties):
    return {
        "type": "object",
        "properties": {
            k: ({"type": v} if isinstance(v, str) else v) for k, v in properties.items()
        },
        "required": list(properties),
    }


STATUS = {"type": "string", "enum": ["P", "A", "OD"]}
ROLE = {"type": "string", "enum": ["STUDENT", "FACULTY", "ADMIN"]}
REQUESTS = {
    "login": obj(institute_id="string", password="string"),
    "refresh": obj(refresh="string"),
    "password_reset": obj(email={"type": "string", "format": "email"}),
    "password_confirm": obj(token="string", new_password="string"),
    "submit": obj(records={"type": "array", "items": obj(student_id="integer", status=STATUS)}),
    "record_edit": obj(status=STATUS, reason="string"),
    "corrections": obj(record_id="integer", requested_status=STATUS, reason="string"),
    "correction_decide": obj(
        decision={"type": "string", "enum": ["APPROVE", "REJECT"]}, note="string"
    ),
    "course_list": obj(code="string", title="string"),
    "sections": obj(course_id="integer", faculty_id="integer", name="string"),
    "timetable": obj(section_id="integer", weekday="integer", start="string", end="string"),
    "enroll": obj(csv="string"),
    "users": obj(
        institute_id="string", name="string", email="string", password="string", role=ROLE
    ),
    "user_edit": {"type": "object", "properties": {"role": ROLE, "is_active": {"type": "boolean"}}},
    "config": obj(threshold="number"),
}
ERROR = obj(error=obj(code="string", message="string", details="object"))
