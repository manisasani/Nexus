# core/middleware.py
import uuid
import logging

logger = logging.getLogger("django.request")


class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = str(uuid.uuid4())
        request.request_id = request_id

        response = self.get_response(request)
        response["X-Request-ID"] = request_id

        logger.info(
            "request_id=%s method=%s path=%s status=%s",
            request_id, request.method, request.path, response.status_code
        )

        return response