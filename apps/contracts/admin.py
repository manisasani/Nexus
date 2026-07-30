from django.contrib import admin
from django.utils.html import format_html
from .models import Contract, ContractEvent


class ContractEventInline(admin.TabularInline):
    model = ContractEvent
    extra = 0
    readonly_fields = ("from_status", "to_status", "triggered_by", "note", "created_at")
    can_delete = False
    ordering = ("created_at",)

    def has_add_permission(self, request, obj=None):
        return False  


STATUS_COLORS = {
    "ACTIVE": "#2563eb",
    "DELIVERED": "#f59e0b",
    "COMPLETED": "#16a34a",
    "DISPUTED": "#dc2626",
    "CANCELLED": "#6b7280",
}


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = (
        "id", "project_title", "client", "freelancer",
        "agreed_price", "status_badge", "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("project__title", "client__email", "freelancer__email")
    autocomplete_fields = ("project", "proposal", "client", "freelancer")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
    inlines = [ContractEventInline]
    list_select_related = ("project", "client", "freelancer")

    fieldsets = (
        ("Parties", {"fields": ("client", "freelancer")}),
        ("Contract Details", {"fields": ("project", "proposal", "agreed_price", "status")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="Project")
    def project_title(self, obj):
        return obj.project.title

    @admin.display(description="Status")
    def status_badge(self, obj):
        color = STATUS_COLORS.get(obj.status, "#000")
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 10px; '
            'border-radius: 10px; font-size: 11px; font-weight: 600;">{}</span>',
            color, obj.status,
        )

    def has_add_permission(self, request):
        return False  


@admin.register(ContractEvent)
class ContractEventAdmin(admin.ModelAdmin):
    list_display = ("id", "contract", "from_status", "to_status", "triggered_by", "created_at")
    list_filter = ("to_status", "created_at")
    search_fields = ("contract__project__title", "triggered_by__email")
    readonly_fields = ("contract", "from_status", "to_status", "triggered_by", "note", "created_at")
    list_select_related = ("contract", "triggered_by")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False  