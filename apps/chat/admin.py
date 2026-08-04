from django.contrib import admin
from .models import ChatRoom, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("sender", "content", "read_at", "created_at")
    can_delete = False
    ordering = ("created_at",)

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ("id", "contract_link", "participants", "message_count", "created_at")
    search_fields = ("contract__project__title", "contract__client__email", "contract__freelancer__email")
    readonly_fields = ("contract", "created_at")
    list_select_related = ("contract", "contract__client", "contract__freelancer")
    inlines = [MessageInline]

    @admin.display(description="Contract")
    def contract_link(self, obj):
        return f"Contract #{obj.contract_id}"

    @admin.display(description="Participants")
    def participants(self, obj):
        return f"{obj.contract.client.email} ↔ {obj.contract.freelancer.email}"

    @admin.display(description="Messages")
    def message_count(self, obj):
        return obj.messages.count()

    def has_add_permission(self, request):
        return False 


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "sender", "content_preview", "is_read", "created_at")
    list_filter = ("created_at",)
    search_fields = ("sender__email", "content", "room__contract__project__title")
    readonly_fields = ("room", "sender", "content", "read_at", "created_at")
    list_select_related = ("room", "sender")
    date_hierarchy = "created_at"

    @admin.display(description="Message")
    def content_preview(self, obj):
        return obj.content[:60] + ("…" if len(obj.content) > 60 else "")

    @admin.display(description="Read", boolean=True)
    def is_read(self, obj):
        return obj.read_at is not None

    def has_add_permission(self, request):
        return False 

    def has_change_permission(self, request, obj=None):
        return False  