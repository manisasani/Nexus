import hashlib
import random
import string
from django.core.cache import cache

CODE_TTL_SECONDS = 600  


class TelegramLinkService:

    @staticmethod
    def _cache_key(code_hash):
        return f"telegram_link:{code_hash}"

    @staticmethod
    def _hash_code(code):
        return hashlib.sha256(code.encode()).hexdigest()

    @staticmethod
    def generate_link_code(user):
        code = "".join(random.choices(string.digits, k=6))
        hashed = TelegramLinkService._hash_code(code)
        cache.set(TelegramLinkService._cache_key(hashed), user.id, timeout=CODE_TTL_SECONDS)
        return code

    @staticmethod
    def resolve_code(code):
        """
        Returns the user_id linked to this code, or None if invalid/expired.
        Consumes the code (single-use).
        """
        hashed = TelegramLinkService._hash_code(code)
        key = TelegramLinkService._cache_key(hashed)
        user_id = cache.get(key)
        if user_id is not None:
            cache.delete(key)
        return user_id