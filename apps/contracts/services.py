# apps/contracts/services.py
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.projects.models import Project, Proposal
from .models import Contract, ContractEvent
from apps.wallets.services import WalletService
from apps.wallets.models import Wallet


class ProposalService:

    @staticmethod
    @transaction.atomic
    def accept(proposal_id, actor):
        """
        Accepts a proposal: creates a Contract, rejects competing proposals,
        closes the project. Idempotent and safe under concurrent access.
        """
        proposal = Proposal.objects.select_for_update().get(id=proposal_id)
        project = Project.objects.select_for_update().get(id=proposal.project_id)

        
        if project.owner_id != actor.id:
            raise PermissionError("Only the project owner can accept a proposal.")

    
        if hasattr(project, "contract"):
            existing_contract = project.contract
            if proposal.status == Proposal.Status.ACCEPTED:
            
                return existing_contract
            raise ValidationError("This project already has a contract.")

        if proposal.status != Proposal.Status.PENDING:
            raise ValidationError(f"Cannot accept a proposal with status {proposal.status}.")

        if project.status != Project.Status.OPEN:
            raise ValidationError("Cannot accept a proposal on a project that is not OPEN.")

    
        contract = Contract.objects.create(
            project=project,
            proposal=proposal,
            client=project.owner,
            freelancer=proposal.freelancer,
            agreed_price=proposal.bid_amount,
            status=Contract.Status.ACTIVE,
        )

        ContractEvent.objects.create(
            contract=contract,
            from_status="",
            to_status=Contract.Status.ACTIVE,
            triggered_by=actor,
            note="Contract created from accepted proposal.",
        )

        
        proposal.status = Proposal.Status.ACCEPTED
        proposal.save(update_fields=["status"])

        
        Proposal.objects.filter(
            project=project, status=Proposal.Status.PENDING
        ).exclude(id=proposal.id).update(status=Proposal.Status.REJECTED)

        
        project.status = Project.Status.CLOSED
        project.save(update_fields=["status"])

        return contract
    


class ContractService:

    VALID_TRANSITIONS = {
        Contract.Status.ACTIVE: [Contract.Status.DELIVERED, Contract.Status.CANCELLED],
        Contract.Status.DELIVERED: [Contract.Status.COMPLETED, Contract.Status.DISPUTED],
        Contract.Status.COMPLETED: [],
        Contract.Status.DISPUTED: [],
        Contract.Status.CANCELLED: [],
    }

    @staticmethod
    @transaction.atomic
    def _transition(contract_id, actor, new_status, allowed_roles, note=""):
        contract = Contract.objects.select_for_update().get(id=contract_id)

        
        if actor.id not in (
            contract.client_id if "client" in allowed_roles else None,
            contract.freelancer_id if "freelancer" in allowed_roles else None,
        ):
            raise PermissionError("You are not allowed to perform this action.")

        
        if contract.status == new_status:
            return contract

        
        allowed_next = ContractService.VALID_TRANSITIONS.get(contract.status, [])
        if new_status not in allowed_next:
            raise ValidationError(
                f"Cannot transition from {contract.status} to {new_status}."
            )

        old_status = contract.status
        contract.status = new_status
        contract.save(update_fields=["status"])

        ContractEvent.objects.create(
            contract=contract,
            from_status=old_status,
            to_status=new_status,
            triggered_by=actor,
            note=note,
        )

        return contract

    @staticmethod
    def mark_delivered(contract_id, actor):
        return ContractService._transition(
            contract_id, actor, Contract.Status.DELIVERED, allowed_roles=["freelancer"]
        )

    @staticmethod
    @transaction.atomic
    def mark_completed(contract_id, actor):
        contract = ContractService._transition(
            contract_id, actor, Contract.Status.COMPLETED, allowed_roles=["client"]
        )

        
        if contract.status == Contract.Status.COMPLETED:
            client_wallet = Wallet.objects.get(user_id=contract.client_id)
            freelancer_wallet = Wallet.objects.get(user_id=contract.freelancer_id)

            amount_cents = int(contract.agreed_price * 100)  

            WalletService.transfer(
                from_wallet_id=client_wallet.id,
                to_wallet_id=freelancer_wallet.id,
                amount=amount_cents,
                reference=f"Contract #{contract.id} settlement",
                idempotency_key=f"contract-settlement:{contract.id}",
            )

        return contract

    @staticmethod
    def cancel(contract_id, actor, note=""):
        return ContractService._transition(
            contract_id, actor, Contract.Status.CANCELLED, allowed_roles=["client", "freelancer"], note=note
        )

    @staticmethod
    def raise_dispute(contract_id, actor, note=""):
        return ContractService._transition(
            contract_id, actor, Contract.Status.DISPUTED, allowed_roles=["client", "freelancer"], note=note
        )