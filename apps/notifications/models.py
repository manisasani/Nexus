from django.db import models
from django.conf import settings


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        NEW_PROPOSAL = "NEW_PROPOSAL", "New Proposal"
        PROPOSAL_ACCEPTED = "PROPOSAL_ACCEPTED", "Proposal Accepted"
        CONTRACT_DELIVERED = "CONTRACT_DELIVERED", "Contract Delivered"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="notifications", on_delete=models.CASCADE
    )
    notification_type = models.CharField(max_length=32, choices=NotificationType.choices)
    message = models.CharField(max_length=255)
    reference = models.CharField(max_length=255, blank=True)  # مثلاً "contract:42"
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.notification_type} -> {self.recipient.email}"


class TelegramLink(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name="telegram_link", on_delete=models.CASCADE
    )
    chat_id = models.BigIntegerField(unique=True)
    linked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Telegram link for {self.user.email}"