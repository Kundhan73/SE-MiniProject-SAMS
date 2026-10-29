from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_handler


class DomainError(APIException):
    def __init__(self, code, message, status=400):
        self.status_code = status
        self.detail = {"code": code, "message": message}


def exception_handler(exc, context):
    if isinstance(exc, DomainError):
        return Response({"error": {**exc.detail, "details": {}}}, status=exc.status_code)
    if isinstance(exc, DjangoValidationError):
        return Response(
            {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "; ".join(exc.messages),
                    "details": {},
                }
            },
            status=400,
        )
    if isinstance(exc, IntegrityError):
        return Response(
            {
                "error": {
                    "code": "CONFLICT",
                    "message": "This operation conflicts with an existing record.",
                    "details": {},
                }
            },
            status=409,
        )
    response = drf_handler(exc, context)
    if response is not None:
        response.data = {
            "error": {
                "code": getattr(exc, "default_code", "INVALID_REQUEST").upper(),
                "message": str(getattr(exc, "detail", "Request rejected")),
                "details": response.data,
            }
        }
    return response
