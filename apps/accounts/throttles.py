from rest_framework.throttling import AnonRateThrottle, SimpleRateThrottle

class LoginThrottle(AnonRateThrottle):
    scope = 'login'

class RegisterThrottle(AnonRateThrottle):
    scope = 'register'

class OTPRequestThrottle(SimpleRateThrottle):
    scope = "otp_request"

    def get_cache_key(self, request, view):
        phone = request.data.get("phone_number", "")
        ident = phone if phone else self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}


class OTPVerifyThrottle(SimpleRateThrottle):
    scope = "otp_verify"

    def get_cache_key(self, request, view):
        phone = request.data.get("phone_number", "")
        ident = phone if phone else self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}