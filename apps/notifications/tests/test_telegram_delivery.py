import pytest
from unittest.mock import patch
from unittest.mock import patch, AsyncMock
from apps.accounts.factories import ClientFactory
from apps.notifications.models import NotificationPreference, TelegramLink
from apps.notifications.tasks import send_telegram_notification
from django.test import override_settings


@pytest.mark.django_db
class TestTelegramDeliveryRespectsPreferences:
    @patch("apps.notifications.tasks.Bot")
    def test_message_not_sent_when_disabled(self, mock_bot):
        user = ClientFactory()
        NotificationPreference.objects.filter(user=user).update(telegram_enabled=False)
        TelegramLink.objects.create(user=user, chat_id=12345)

        send_telegram_notification(user.id, "test message")

        mock_bot.return_value.send_message.assert_not_called()

    @patch("apps.notifications.tasks.Bot")
    def test_message_not_sent_when_not_linked(self, mock_bot):
        user = ClientFactory()
        NotificationPreference.objects.filter(user=user).update(telegram_enabled=True)

        send_telegram_notification(user.id, "test message")

        mock_bot.return_value.send_message.assert_not_called()

    @override_settings(TELEGRAM_BOT_TOKEN="fake-token-for-test")
    @patch("apps.notifications.tasks.Bot")
    def test_message_sent_when_enabled_and_linked(self, mock_bot):
        mock_bot.return_value.send_message = AsyncMock()

        user = ClientFactory()
        NotificationPreference.objects.filter(user=user).update(telegram_enabled=True)
        TelegramLink.objects.create(user=user, chat_id=12345)

        send_telegram_notification(user.id, "test message")

        mock_bot.return_value.send_message.assert_called_once()

    @patch("apps.notifications.tasks.Bot")
    def test_message_not_sent_in_digest_mode(self, mock_bot):
        user = ClientFactory()
        NotificationPreference.objects.filter(user=user).update(
            telegram_enabled=True, digest_mode=True
        )
        TelegramLink.objects.create(user=user, chat_id=12345)

        send_telegram_notification(user.id, "test message")

        mock_bot.return_value.send_message.assert_not_called()