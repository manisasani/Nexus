# apps/contracts/services.py
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.projects.models import Project, Proposal
from .models import Contract, ContractEvent


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