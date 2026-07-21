from rest_framework import serializers
from .models import Wallet, LedgerEntry


class WalletSerializer(serializers.ModelSerializer):
    balance_display = serializers.SerializerMethodField()

    class Meta:
        model = Wallet
        fields = ("id", "balance", "balance_display", "updated_at")
        read_only_fields = fields

    def get_balance_display(self, obj):
        return f"${obj.balance / 100:.2f}"


class LedgerEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LedgerEntry
        fields = (
            "id", "entry_type", "amount", "reference",
            "balance_after", "created_at",
        )
        read_only_fields = fields