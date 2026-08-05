import pytest
from apps.accounts.factories import ClientFactory
from apps.notifications.services.telegram_link_service import TelegramLinkService
from apps.notifications.models import TelegramLink


@pytest.mark.django_db
class TestTelegramLinkSecurity:
    def test_valid_code_links_correct_user(self):
        user = ClientFactory()
        code = TelegramLinkService.generate_link_code(user)

        resolved_user_id = TelegramLinkService.resolve_code(code)
        assert resolved_user_id == user.id

    def test_code_is_single_use(self):
        user = ClientFactory()
        code = TelegramLinkService.generate_link_code(user)

        TelegramLinkService.resolve_code(code)
        second_attempt = TelegramLinkService.resolve_code(code)  

        assert second_attempt is None

    def test_invalid_code_returns_none(self):
        result = TelegramLinkService.resolve_code("000000")
        assert result is None

    def test_chat_id_never_settable_via_api(self):
        from apps.notifications.serializers import NotificationPreferenceSerializer
        assert "chat_id" not in NotificationPreferenceSerializer().fields