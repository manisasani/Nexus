from django.contrib import admin
from django.utils.html import format_html
from .models import Wallet, LedgerEntry


class LedgerEntryInline(admin.TabularInline):
    model = LedgerEntry
    extra = 0
    readonly_fields = ("entry_type", "amount", "reference", "balance_after", "created_at")
    can_delete = False
    ordering = ("-created_at",)

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "balance_display", "updated_at")
    search_fields = ("user__email",)
    readonly_fields = ("balance", "created_at", "updated_at")
    inlines = [LedgerEntryInline]
    list_select_related = ("user",)

    @admin.display(description="Balance", ordering="balance")
    def balance_display(self, obj):
        return f"${obj.balance / 100:,.2f}"

    def has_add_permission(self, request):
        return False  

    def has_delete_permission(self, request, obj=None):
        return False


ENTRY_TYPE_COLORS = {
    "CREDIT": "#16a34a",
    "DEBIT": "#dc2626",
}


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = (
        "id", "wallet_user", "entry_type_badge", "amount_display",
        "reference", "balance_after_display", "created_at",
    )
    list_filter = ("entry_type", "created_at")
    search_fields = ("wallet__user__email", "reference", "idempotency_key")
    readonly_fields = (
        "wallet", "entry_type", "amount", "reference",
        "idempotency_key", "balance_after", "created_at",
    )
    date_hierarchy = "created_at"
    list_select_related = ("wallet", "wallet__user")

    @admin.display(description="User")
    def wallet_user(self, obj):
        return obj.wallet.user.email

    @admin.display(description="Type")
    def entry_type_badge(self, obj):
        color = ENTRY_TYPE_COLORS.get(obj.entry_type, "#000")
        sign = "+" if obj.entry_type == "CREDIT" else "−"
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 10px; '
            'border-radius: 10px; font-size: 11px; font-weight: 600;">{} {}</span>',
            color, sign, obj.entry_type,
        )

    @admin.display(description="Amount")
    def amount_display(self, obj):
        return f"${obj.amount / 100:,.2f}"

    @admin.display(description="Balance After")
    def balance_after_display(self, obj):
        return f"${obj.balance_after / 100:,.2f}"

    def has_add_permission(self, request):
        return False  

    def has_change_permission(self, request, obj=None):
        return False  

    def has_delete_permission(self, request, obj=None):
        return False