import hashlib
import random
import string
import logging
from django.core.cache import cache
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

OTP_LENGTH = 6
OTP_TTL_SECONDS = 300 
OTP_MAX_ATTEMPTS = 5


class OTPService:

    @staticmethod
    def _cache_key(phone_number):
        return f"otp:{phone_number}"

    @staticmethod
    def _attempts_key(phone_number):
        return f"otp_attempts:{phone_number}"

    @staticmethod
    def _hash_otp(otp_code):
        return hashlib.sha256(otp_code.encode()).hexdigest()

    @staticmethod
    def generate_and_store(phone_number):
        """
        Generates a random OTP, hashes it, stores the hash in Redis with TTL.
        Returns the PLAINTEXT code — caller is responsible for sending it
        via SMS and MUST NOT log it.
        """
        otp_code = "".join(random.choices(string.digits, k=OTP_LENGTH))
        hashed = OTPService._hash_otp(otp_code)

        cache.set(OTPService._cache_key(phone_number), hashed, timeout=OTP_TTL_SECONDS)
        
        cache.delete(OTPService._attempts_key(phone_number))

        logger.info(f"OTP generated for phone ending in ...{phone_number[-4:]}")  # هرگز کد رو لاگ نکن!
        return otp_code

    @staticmethod
    def verify(phone_number, submitted_code):
        """
        Verifies a submitted OTP against the stored hash.
        Enforces a max-attempts limit to prevent brute-force guessing.
        """
        attempts_key = OTPService._attempts_key(phone_number)
        attempts = cache.get(attempts_key, 0)

        if attempts >= OTP_MAX_ATTEMPTS:
            raise ValidationError("Too many failed attempts. Request a new code.")

        stored_hash = cache.get(OTPService._cache_key(phone_number))
        if stored_hash is None:
            raise ValidationError("Code expired or not found. Request a new one.")

        submitted_hash = OTPService._hash_otp(submitted_code)

        if submitted_hash != stored_hash:
            cache.set(attempts_key, attempts + 1, timeout=OTP_TTL_SECONDS)
            raise ValidationError("Invalid code.")

        
        cache.delete(OTPService._cache_key(phone_number))
        cache.delete(attempts_key)
        return True