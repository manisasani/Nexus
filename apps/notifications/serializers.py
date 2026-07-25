from rest_framework import serializers
from .models import Notification

class NotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("id", "notification_type", "message", "reference", "is_read", "created_at")
        read_only_fields = fields