import pytest
from apps.projects.factories import OpenProjectFactory, ProposalFactory
from apps.contracts.services import ProposalService
from apps.contracts.models import Contract


@pytest.mark.django_db
class TestAcceptIdempotency:
    def test_accepting_same_proposal_twice_is_safe(self):
        project = OpenProjectFactory()
        proposal = ProposalFactory(project=project)

        contract1 = ProposalService.accept(proposal_id=proposal.id, actor=project.owner)
        contract2 = ProposalService.accept(proposal_id=proposal.id, actor=project.owner)

        assert contract1.id == contract2.id
        assert Contract.objects.filter(project=project).count() == 1

    def test_accepting_different_proposal_after_accept_fails(self):
        project = OpenProjectFactory()
        proposal1 = ProposalFactory(project=project)
        proposal2 = ProposalFactory(project=project)

        ProposalService.accept(proposal_id=proposal1.id, actor=project.owner)

        with pytest.raises(Exception):  
            ProposalService.accept(proposal_id=proposal2.id, actor=project.owner)