from django.contrib import admin
from django.utils.html import format_html
from .models import Ticket, TicketMessage


class TicketMessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 1
    fields = ("author", "body", "is_staff_reply", "created_at")
    readonly_fields = ("created_at",)
    ordering = ("created_at",)


STATUS_COLORS = {
    "OPEN": "#2563eb",
    "IN_PROGRESS": "#f59e0b",
    "RESOLVED": "#16a34a",
    "CLOSED": "#6b7280",
}

CATEGORY_ICONS = {
    "GENERAL": "💬",
    "PAYMENT": "💳",
    "DISPUTE": "⚠️",
    "TECHNICAL": "🛠️",
}


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id", "subject", "category_display", "status_badge",
        "opened_by", "contract_link", "created_at",
    )
    list_filter = ("status", "category", "created_at")
    search_fields = ("subject", "opened_by__email", "resolution")
    autocomplete_fields = ("opened_by", "contract")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
    inlines = [TicketMessageInline]
    list_select_related = ("opened_by", "contract")

    fieldsets = (
        ("Ticket Info", {"fields": ("subject", "category", "status")}),
        ("People & Links", {"fields": ("opened_by", "contract")}),
        ("Resolution", {"fields": ("resolution",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="Category")
    def category_display(self, obj):
        icon = CATEGORY_ICONS.get(obj.category, "")
        return f"{icon} {obj.get_category_display()}"

    @admin.display(description="Status")
    def status_badge(self, obj):
        color = STATUS_COLORS.get(obj.status, "#000")
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 10px; '
            'border-radius: 10px; font-size: 11px; font-weight: 600;">{}</span>',
            color, obj.get_status_display(),
        )

    @admin.display(description="Contract")
    def contract_link(self, obj):
        if obj.contract:
            return f"Contract #{obj.contract_id}"
        return "—"


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "ticket", "author", "is_staff_reply", "body_preview", "created_at")
    list_filter = ("is_staff_reply", "created_at")
    search_fields = ("ticket__subject", "author__email", "body")
    readonly_fields = ("created_at",)
    list_select_related = ("ticket", "author")

    @admin.display(description="Message")
    def body_preview(self, obj):
        return obj.body[:60] + ("…" if len(obj.body) > 60 else "")