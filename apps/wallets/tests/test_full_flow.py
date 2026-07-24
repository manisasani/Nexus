import pytest
from apps.projects.factories import OpenProjectFactory, ProposalFactory
from apps.contracts.services import ProposalService, ContractService
from apps.wallets.models import Wallet
from apps.wallets.services import WalletService


@pytest.mark.django_db
class TestFullPaymentFlow:
    def test_deposit_contract_payment_freelancer_receives_funds(self):
        project = OpenProjectFactory(budget="500.00")
        proposal = ProposalFactory(project=project, bid_amount="500.00")

        client_wallet, _ = Wallet.objects.get_or_create(user=project.owner)
        freelancer_wallet, _ = Wallet.objects.get_or_create(user=proposal.freelancer)

        
        WalletService.credit(client_wallet.id, 50000, "initial deposit", "deposit-1")

        
        contract = ProposalService.accept(proposal_id=proposal.id, actor=project.owner)
        contract = ContractService.mark_delivered(contract.id, actor=contract.freelancer)
        contract = ContractService.mark_completed(contract.id, actor=contract.client)

        client_wallet.refresh_from_db()
        freelancer_wallet.refresh_from_db()

        assert client_wallet.balance == 0       
        assert freelancer_wallet.balance == 50000  