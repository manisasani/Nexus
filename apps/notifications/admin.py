from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "recipient", "notification_type", "message_preview", "is_read", "created_at")
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = ("recipient__email", "message", "reference")
    readonly_fields = ("recipient", "notification_type", "message", "reference", "created_at")
    list_select_related = ("recipient",)
    list_editable = ()  

    @admin.display(description="Message")
    def message_preview(self, obj):
        return obj.message[:60] + ("…" if len(obj.message) > 60 else "")

    def has_add_permission(self, request):
        return False 