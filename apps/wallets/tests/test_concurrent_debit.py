import pytest
import threading
from django.db import connections
from apps.accounts.factories import ClientFactory
from apps.wallets.models import Wallet, LedgerEntry
from apps.wallets.services import WalletService


@pytest.mark.django_db(transaction=True)
class TestConcurrentDebit:
    @pytest.mark.skip(reason="SQLite threading/locking behavior unreliable for this test; verify against PostgreSQL directly")
    def test_two_simultaneous_debits_cannot_overdraw(self):

        user = ClientFactory()
        wallet = Wallet.objects.get(user=user)
        wallet.balance = 10000
        wallet.save()

        results = []
        errors = []

        def try_debit(key_suffix):
            try:
                entry = WalletService.debit(
                    wallet.id, 7000, "concurrent test", f"debit-{key_suffix}"
                )
                results.append(entry)
            except Exception as e:
                errors.append(e)
            finally:
                connections.close_all()

        t1 = threading.Thread(target=try_debit, args=("a",))
        t2 = threading.Thread(target=try_debit, args=("b",))

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        wallet.refresh_from_db()

        
        assert len(results) == 1
        assert len(errors) == 1

        
        assert wallet.balance == 3000
        assert wallet.balance >= 0