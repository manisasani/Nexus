from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


ERROR_CODE_MAP = {
    400: "validation_error",
    401: "authentication_failed",
    403: "permission_denied",
    404: "not_found",
    405: "method_not_allowed",
    429: "throttled",
    500: "server_error",
}


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        # یک استثنای پیش‌بینی‌نشده که DRF خودش نمی‌شناسه (مثلاً یک باگ واقعی)
        return Response(
            {
                "detail": "An unexpected error occurred.",
                "code": "server_error",
                "errors": {},
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    code = ERROR_CODE_MAP.get(response.status_code, "error")

    # اگه response.data خودش یک دیکشنری از خطاهای فیلد به فیلد بود (مثل ValidationError معمولی)
    if isinstance(response.data, dict) and "detail" not in response.data:
        errors = response.data
        detail = "Validation failed." if response.status_code == 400 else "Request failed."
    else:
        errors = {}
        detail = response.data.get("detail", "Request failed.") if isinstance(response.data, dict) else str(response.data)

    response.data = {
        "detail": str(detail),
        "code": code,
        "errors": errors,
        "request_id": getattr(context["request"], "request_id", None),
    }
    return response