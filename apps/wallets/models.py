from django.db import models
from django.conf import settings


class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name="wallet", on_delete=models.PROTECT
    )
    balance = models.BigIntegerField(default=0)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(balance__gte=0),
                name="wallet_balance_never_negative",
            )
        ]

    def __str__(self):
        return f"Wallet({self.user.email}): {self.balance} cents"
    
class LedgerEntry(models.Model):
    class EntryType(models.TextChoices):
        CREDIT = "CREDIT", "Credit"
        DEBIT = "DEBIT", "Debit"

    wallet = models.ForeignKey(Wallet, related_name="entries", on_delete=models.PROTECT)
    entry_type = models.CharField(max_length=6, choices=EntryType.choices)
    amount = models.BigIntegerField()
    reference = models.CharField(max_length=255)  
    idempotency_key = models.CharField(max_length=255, unique=True)
    balance_after = models.BigIntegerField()  
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="ledger_amount_always_positive",
        )
        ]

    def __str__(self):
        return f"{self.entry_type} {self.amount} on {self.wallet}"

