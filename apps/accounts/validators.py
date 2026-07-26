import re
from django.core.exceptions import ValidationError


def validate_e164_phone(value):
    pattern = r"^\+[1-9]\d{6,14}$"
    if not re.match(pattern, value):
        raise ValidationError(
            "Phone numver must be in E.164 format (e.g. +989123456789)"
        )