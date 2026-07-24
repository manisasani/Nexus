import pytest
from django.core.exceptions import ValidationError
from apps.accounts.factories import ClientFactory
from apps.wallets.models import Wallet
from apps.wallets.services import WalletService


@pytest.mark.django_db
class TestWalletService:
    def test_credit_increases_balance(self):
        user = ClientFactory()
        wallet = Wallet.objects.get(user=user)
        wallet.balance = 0
        wallet.save()

        WalletService.credit(wallet.id, 5000, "test credit", "key-1")

        wallet.refresh_from_db()
        assert wallet.balance == 5000

    def test_debit_decreases_balance(self):
        user = ClientFactory()
        wallet = Wallet.objects.get(user=user)
        wallet.balance = 10000
        wallet.save()

        WalletService.debit(wallet.id, 3000, "test debit", "key-2")

        wallet.refresh_from_db()
        assert wallet.balance == 7000

    def test_debit_exceeding_balance_fails(self):
        user = ClientFactory()
        wallet = Wallet.objects.get(user=user)
        wallet.balance = 1000
        wallet.save()

        with pytest.raises(ValidationError):
            WalletService.debit(wallet.id, 5000, "overdraft attempt", "key-3")

        wallet.refresh_from_db()
        assert wallet.balance == 1000 

    def test_idempotent_credit_does_not_double_charge(self):
        user = ClientFactory()
        wallet = Wallet.objects.get(user=user)
        wallet.balance = 0
        wallet.save()

        WalletService.credit(wallet.id, 5000, "topup", "same-key")
        WalletService.credit(wallet.id, 5000, "topup", "same-key") 

        wallet.refresh_from_db()
        assert wallet.balance == 5000  