from rest_framework import serializers
from .models import Notification, NotificationPreference

class NotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("id", "notification_type", "message", "reference", "is_read", "created_at")
        read_only_fields = fields

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = (
            "email_enabled", "telegram_enabled", "sms_enabled",
            "in_app_enabled", "digest_mode",
        )