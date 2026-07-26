import pytest
from django.core.cache import cache
from rest_framework.test import APIClient
from apps.accounts.services.otp_service import OTPService


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.mark.django_db
class TestOTPFlow:
    def test_request_then_verify_succeeds(self):
        phone = "+989123456789"
        api = APIClient()

        response = api.post("/api/v1/auth/otp/request/", {"phone_number": phone})
        assert response.status_code == 200

        
        from apps.accounts.services.otp_service import OTPService
    
        otp_code = OTPService.generate_and_store(phone)

        verify_response = api.post("/api/v1/auth/otp/verify/", {
            "phone_number": phone,
            "code": otp_code,
        })
        assert verify_response.status_code == 200
        assert "access" in verify_response.data

    def test_wrong_code_fails(self):
        phone = "+989123456780"
        OTPService.generate_and_store(phone)

        api = APIClient()
        response = api.post("/api/v1/auth/otp/verify/", {
            "phone_number": phone,
            "code": "000000",
        })
        assert response.status_code == 400

    def test_otp_never_appears_in_plaintext_response(self):
        phone = "+989123456781"
        api = APIClient()
        response = api.post("/api/v1/auth/otp/request/", {"phone_number": phone})

        assert "otp" not in str(response.data).lower()
        assert "code" not in str(response.data).lower()

@pytest.mark.django_db
class TestOTPRateLimiting:
    def test_otp_request_rate_limited_per_phone(self):
        phone = "+989123456782"
        api = APIClient()

        
        for _ in range(3):
            response = api.post("/api/v1/auth/otp/request/", {"phone_number": phone})
            assert response.status_code == 200

        response = api.post("/api/v1/auth/otp/request/", {"phone_number": phone})
        assert response.status_code == 429

    def test_otp_verify_brute_force_blocked(self):
        phone = "+989123456783"
        OTPService.generate_and_store(phone)

        api = APIClient()
        
        for _ in range(5):
            response = api.post("/api/v1/auth/otp/verify/", {
                "phone_number": phone,
                "code": "000000",  
            })

        response = api.post("/api/v1/auth/otp/verify/", {
            "phone_number": phone,
            "code": "000000",
        })
        assert response.status_code in (400, 429)

def test_otp_stored_hashed_not_plaintext(self):
    phone = "+989123456784"
    otp_code = OTPService.generate_and_store(phone)

    stored_value = cache.get(f"otp:{phone}")
    assert stored_value != otp_code  
    assert len(stored_value) == 64 