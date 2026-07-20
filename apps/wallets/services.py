from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Wallet, LedgerEntry


class WalletService:

    @staticmethod
    @transaction.atomic
    def _apply_entry(wallet_id, entry_type, amount, reference, idempotency_key):
        """
        Core primitive: applies a single ledger entry to a wallet.
        Idempotent, atomic, and safe under concurrent access.
        """
        if amount <= 0:
            raise ValidationError("Amount must be positive.")

        existing = LedgerEntry.objects.filter(idempotency_key=idempotency_key).first()
        if existing:
            return existing

        wallet = Wallet.objects.select_for_update().get(id=wallet_id)

        if entry_type == LedgerEntry.EntryType.DEBIT:
            if wallet.balance < amount:
                raise ValidationError("Insufficient balance.")
            new_balance = wallet.balance - amount
        else:  # CREDIT
            new_balance = wallet.balance + amount

        entry = LedgerEntry.objects.create(
            wallet=wallet,
            entry_type=entry_type,
            amount=amount,
            reference=reference,
            idempotency_key=idempotency_key,
            balance_after=new_balance,
        )

        wallet.balance = new_balance
        wallet.save(update_fields=["balance"])

        return entry

    @staticmethod
    def credit(wallet_id, amount, reference, idempotency_key):
        return WalletService._apply_entry(
            wallet_id, LedgerEntry.EntryType.CREDIT, amount, reference, idempotency_key
        )

    @staticmethod
    def debit(wallet_id, amount, reference, idempotency_key):
        return WalletService._apply_entry(
            wallet_id, LedgerEntry.EntryType.DEBIT, amount, reference, idempotency_key
        )

    @staticmethod
    @transaction.atomic
    def transfer(from_wallet_id, to_wallet_id, amount, reference, idempotency_key):
        """
        Atomically debits one wallet and credits another.
        Uses a combined idempotency key check to avoid partial transfers.
        """
        existing = LedgerEntry.objects.filter(
            idempotency_key=f"{idempotency_key}:debit"
        ).first()
        if existing:
            credit_entry = LedgerEntry.objects.get(idempotency_key=f"{idempotency_key}:credit")
            return existing, credit_entry

        wallet_ids_sorted = sorted([from_wallet_id, to_wallet_id])
        wallets = {
            w.id: w for w in Wallet.objects.select_for_update().filter(id__in=wallet_ids_sorted)
        }

        debit_entry = WalletService.debit(
            from_wallet_id, amount, reference, f"{idempotency_key}:debit"
        )
        credit_entry = WalletService.credit(
            to_wallet_id, amount, reference, f"{idempotency_key}:credit"
        )

        return debit_entry, credit_entry