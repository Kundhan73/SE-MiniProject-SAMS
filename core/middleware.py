import json
import logging
import time
import uuid

logger = logging.getLogger("sams.requests")


class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        started = time.monotonic()
        request_id = uuid.uuid4().hex
        response = self.get_response(request)
        response["X-Request-ID"] = request_id
        # No query strings, payloads, cookies, passwords, reset links or tokens.
        logger.info(
            json.dumps(
                {
                    "request_id": request_id,
                    "user_id": getattr(getattr(request, "user", None), "pk", None),
                    "path": request.path,
                    "method": request.method,
                    "status": response.status_code,
                    "latency_ms": round((time.monotonic() - started) * 1000, 2),
                }
            )
        )
        return response
