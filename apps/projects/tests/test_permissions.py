import pytest
from rest_framework.test import APIClient
from apps.accounts.factories import ClientFactory, FreelancerFactory
from apps.projects.factories import ProjectFactory, OpenProjectFactory, ProposalFactory


@pytest.mark.django_db
class TestProjectCreatePermission:
    def test_client_can_create_project(self):
        client_user = ClientFactory()
        api = APIClient()
        api.force_authenticate(user=client_user)
        response = api.post("/api/v1/projects/", {
            "title": "New project",
            "description": "desc",
            "budget": "300.00",
            "deadline": "2027-01-01",
        })
        assert response.status_code == 201

    def test_freelancer_cannot_create_project(self):
        freelancer = FreelancerFactory()
        api = APIClient()
        api.force_authenticate(user=freelancer)
        response = api.post("/api/v1/projects/", {
            "title": "Should fail",
            "description": "desc",
            "budget": "300.00",
            "deadline": "2027-01-01",
        })
        assert response.status_code == 403


@pytest.mark.django_db
class TestProjectObjectPermission:
    def test_owner_can_update_own_project(self):
        project = ProjectFactory()
        api = APIClient()
        api.force_authenticate(user=project.owner)
        response = api.patch(f"/api/v1/projects/{project.id}/", {"title": "Updated"})
        assert response.status_code == 200

    def test_non_owner_cannot_update_project(self):
        project = ProjectFactory()
        other_client = ClientFactory()
        api = APIClient()
        api.force_authenticate(user=other_client)
        response = api.patch(f"/api/v1/projects/{project.id}/", {"title": "Hijacked"})
        assert response.status_code in (403, 404)  


@pytest.mark.django_db
class TestProposalPermissions:
    def test_client_cannot_bid_on_own_project(self):
        project = OpenProjectFactory()
        api = APIClient()
        api.force_authenticate(user=project.owner)
        response = api.post(f"/api/v1/projects/{project.id}/proposals/", {
            "cover_letter": "Bidding on my own project",
            "bid_amount": "200.00",
        })
        assert response.status_code in (400, 403)

    def test_freelancer_cannot_see_another_freelancers_proposal(self):
        project = OpenProjectFactory()
        proposal = ProposalFactory(project=project)  
        other_freelancer = FreelancerFactory()  

        api = APIClient()
        api.force_authenticate(user=other_freelancer)
        response = api.get(f"/api/v1/projects/{project.id}/proposals/")

        assert response.status_code == 200
        proposal_ids = [p["id"] for p in response.data["results"]]
        assert proposal.id not in proposal_ids 

    def test_project_owner_can_see_all_proposals(self):
        project = OpenProjectFactory()
        proposal1 = ProposalFactory(project=project)
        proposal2 = ProposalFactory(project=project)

        api = APIClient()
        api.force_authenticate(user=project.owner)
        response = api.get(f"/api/v1/projects/{project.id}/proposals/")

        assert response.status_code == 200
        proposal_ids = {p["id"] for p in response.data["results"]}
        assert {proposal1.id, proposal2.id}.issubset(proposal_ids)