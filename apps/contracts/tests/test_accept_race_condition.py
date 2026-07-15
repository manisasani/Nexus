import pytest
import threading
from apps.projects.factories import OpenProjectFactory, ProposalFactory
from apps.contracts.services import ProposalService
from apps.contracts.models import Contract
from django.db import connections


@pytest.mark.django_db(transaction=True)  
class TestAcceptRaceCondition:
    def test_concurrent_accept_only_creates_one_contract(self):
        project = OpenProjectFactory()
        proposal1 = ProposalFactory(project=project)
        proposal2 = ProposalFactory(project=project)

        results = []
        errors = []

        def try_accept(proposal_id):
            try:
                contract = ProposalService.accept(proposal_id=proposal_id, actor=project.owner)
                results.append(contract)
            except Exception as e:
                errors.append(e)
            finally:
                connections.close_all()  

        t1 = threading.Thread(target=try_accept, args=(proposal1.id,))
        t2 = threading.Thread(target=try_accept, args=(proposal2.id,))

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        
        assert Contract.objects.filter(project=project).count() == 1
        
        assert len(errors) >= 1