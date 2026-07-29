import pytest
from rest_framework.test import APIClient
from apps.accounts.factories import ClientFactory


@pytest.mark.django_db
class TestTicketPrivacy:
    def test_user_cannot_see_another_users_ticket_in_list(self):
        user_a = ClientFactory()
        user_b = ClientFactory()

        api = APIClient()
        api.force_authenticate(user=user_a)
        api.post("/api/v1/tickets/", {"subject": "My private issue", "category": "GENERAL"})

        api.force_authenticate(user=user_b)
        response = api.get("/api/v1/tickets/")

        assert response.status_code == 200
        assert response.data["count"] == 0  

    def test_user_cannot_retrieve_another_users_ticket_directly(self):
        user_a = ClientFactory()
        user_b = ClientFactory()

        api = APIClient()
        api.force_authenticate(user=user_a)
        create_response = api.post(
            "/api/v1/tickets/", {"subject": "Private", "category": "GENERAL"}
        )
        ticket_id = create_response.data["id"]

        api.force_authenticate(user=user_b)
        response = api.get(f"/api/v1/tickets/{ticket_id}/")

        assert response.status_code in (403, 404)

    def test_staff_can_see_all_tickets(self):
        from apps.accounts.models import CustomUser
        user_a = ClientFactory()
        staff_user = ClientFactory()
        staff_user.is_staff = True
        staff_user.save()

        api = APIClient()
        api.force_authenticate(user=user_a)
        api.post("/api/v1/tickets/", {"subject": "Issue", "category": "GENERAL"})

        api.force_authenticate(user=staff_user)
        response = api.get("/api/v1/tickets/")

        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_user_cannot_set_own_status_or_resolution(self):
        user = ClientFactory()
        api = APIClient()
        api.force_authenticate(user=user)
        response = api.post("/api/v1/tickets/", {
            "subject": "Test",
            "category": "GENERAL",
            "status": "CLOSED",  
        })
        assert response.data["status"] == "OPEN"  

@pytest.mark.django_db
class TestTicketResolution:
    def test_closing_without_resolution_fails(self):
        from apps.accounts.factories import ClientFactory
        user = ClientFactory()
        staff = ClientFactory()
        staff.is_staff = True
        staff.save()

        api = APIClient()
        api.force_authenticate(user=user)
        create_response = api.post(
            "/api/v1/tickets/", {"subject": "Issue", "category": "GENERAL"}
        )
        ticket_id = create_response.data["id"]

        api.force_authenticate(user=staff)
        response = api.patch(f"/api/v1/tickets/{ticket_id}/", {"status": "CLOSED"})

        assert response.status_code == 400

@pytest.mark.django_db
class TestDisputeCreatesTicket:
    def test_raising_dispute_auto_creates_ticket(self):
        from apps.projects.factories import OpenProjectFactory, ProposalFactory
        from apps.contracts.services import ProposalService, ContractService
        from apps.tickets.models import Ticket

        project = OpenProjectFactory()
        proposal = ProposalFactory(project=project)
        contract = ProposalService.accept(proposal_id=proposal.id, actor=project.owner)
        contract = ContractService.mark_delivered(contract.id, actor=contract.freelancer)

        ContractService.raise_dispute(contract.id, actor=contract.client, note="Not as agreed.")

        ticket = Ticket.objects.filter(contract=contract, category=Ticket.Category.DISPUTE).first()
        assert ticket is not None
        assert ticket.opened_by == contract.client