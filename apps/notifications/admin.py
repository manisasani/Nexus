from django.contrib import admin
from .models import Notification, TelegramLink, NotificationPreference


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


@admin.register(TelegramLink)
class TelegramLinkAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "chat_id_masked", "linked_at")
    search_fields = ("user__email",)
    readonly_fields = ("user", "chat_id", "linked_at")
    list_select_related = ("user",)

    @admin.display(description="Chat ID")
    def chat_id_masked(self, obj):
    
        chat_id_str = str(obj.chat_id)
        return f"...{chat_id_str[-4:]}"

    def has_add_permission(self, request):
        return False  

    def has_change_permission(self, request, obj=None):
        return False  


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = (
        "user", "email_enabled", "telegram_enabled",
        "sms_enabled", "in_app_enabled", "digest_mode",
    )
    list_filter = ("email_enabled", "telegram_enabled", "sms_enabled", "digest_mode")
    search_fields = ("user__email",)
    list_select_related = ("user",)

    def has_add_permission(self, request):
        return False  