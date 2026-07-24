import pytest
from rest_framework.test import APIClient
from apps.projects.factories import OpenProjectFactory, ProposalFactory
from apps.contracts.services import ProposalService, ContractService
from apps.contracts.models import Contract
from apps.wallets.models import Wallet
from apps.wallets.services import WalletService


@pytest.mark.django_db
class TestFullHappyPath:
    def test_post_project_propose_accept_deliver_complete(self):
        project = OpenProjectFactory()
        proposal = ProposalFactory(project=project)
        client_wallet = Wallet.objects.get(user=project.owner)
        WalletService.credit(client_wallet.id, 100000, "test funding", "fund-happy-path")

        # Accept
        contract = ProposalService.accept(proposal_id=proposal.id, actor=project.owner)
        assert contract.status == Contract.Status.ACTIVE

        # Deliver (فقط فریلنسر)
        contract = ContractService.mark_delivered(contract.id, actor=contract.freelancer)
        assert contract.status == Contract.Status.DELIVERED

        # Complete (فقط کلاینت)
        contract = ContractService.mark_completed(contract.id, actor=contract.client)
        assert contract.status == Contract.Status.COMPLETED

        # Audit trail باید 3 رویداد داشته باشه
        assert contract.events.count() == 3


@pytest.mark.django_db
class TestInvalidTransitions:
    def test_freelancer_cannot_mark_completed(self):
        project = OpenProjectFactory()
        proposal = ProposalFactory(project=project)
        contract = ProposalService.accept(proposal_id=proposal.id, actor=project.owner)
        contract = ContractService.mark_delivered(contract.id, actor=contract.freelancer)

        with pytest.raises(PermissionError):
            ContractService.mark_completed(contract.id, actor=contract.freelancer)

    def test_client_cannot_mark_delivered(self):
        project = OpenProjectFactory()
        proposal = ProposalFactory(project=project)
        contract = ProposalService.accept(proposal_id=proposal.id, actor=project.owner)

        with pytest.raises(PermissionError):
            ContractService.mark_delivered(contract.id, actor=contract.client)

    def test_cannot_complete_before_delivered(self):
        project = OpenProjectFactory()
        proposal = ProposalFactory(project=project)
        contract = ProposalService.accept(proposal_id=proposal.id, actor=project.owner)

        with pytest.raises(Exception):  # ValidationError: ACTIVE -> COMPLETED مجاز نیست
            ContractService.mark_completed(contract.id, actor=contract.client)

    def test_cannot_transition_from_completed(self):
        project = OpenProjectFactory()
        proposal = ProposalFactory(project=project)
        client_wallet = Wallet.objects.get(user=project.owner)
        WalletService.credit(client_wallet.id, 100000, "test funding", "fund-invalid-transition")
        contract = ProposalService.accept(proposal_id=proposal.id, actor=project.owner)
        contract = ContractService.mark_delivered(contract.id, actor=contract.freelancer)
        contract = ContractService.mark_completed(contract.id, actor=contract.client)

        with pytest.raises(Exception):
            ContractService.mark_delivered(contract.id, actor=contract.freelancer)


@pytest.mark.django_db
class TestAcceptSideEffects:
    def test_accept_rejects_competing_proposals(self):
        project = OpenProjectFactory()
        accepted_proposal = ProposalFactory(project=project)
        rejected_proposal = ProposalFactory(project=project)

        ProposalService.accept(proposal_id=accepted_proposal.id, actor=project.owner)

        rejected_proposal.refresh_from_db()
        assert rejected_proposal.status == "REJECTED"

    def test_accept_closes_project(self):
        project = OpenProjectFactory()
        proposal = ProposalFactory(project=project)

        ProposalService.accept(proposal_id=proposal.id, actor=project.owner)

        project.refresh_from_db()
        assert project.status == "CLOSED"

@pytest.mark.django_db
class TestContractAPI:
    def test_accept_proposal_via_api_returns_201_with_contract(self):
        project = OpenProjectFactory()
        proposal = ProposalFactory(project=project)

        api = APIClient()
        api.force_authenticate(user=project.owner)
        response = api.post(f"/api/v1/projects/{project.id}/proposals/{proposal.id}/accept/")

        assert response.status_code == 201
        assert response.data["status"] == "ACTIVE"

    def test_mark_delivered_via_api(self):
        project = OpenProjectFactory()
        proposal = ProposalFactory(project=project)
        contract = ProposalService.accept(proposal_id=proposal.id, actor=project.owner)

        api = APIClient()
        api.force_authenticate(user=contract.freelancer)
        response = api.post(f"/api/v1/contracts/{contract.id}/deliver/")

        assert response.status_code == 200
        assert response.data["status"] == "DELIVERED"
