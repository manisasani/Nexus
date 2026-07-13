import pytest
from django.db import IntegrityError
from rest_framework.test import APIClient
from apps.projects.factories import OpenProjectFactory, ProposalFactory
from apps.accounts.factories import FreelancerFactory

@pytest.mark.django_db
class TestProposalUniqueness:
    def test_duplicate_proposal_blacked_at_db_level(self):
        project = OpenProjectFactory()
        freelancer = FreelancerFactory()
        ProposalFactory(project=project, freelancer=freelancer)

        with pytest.raises(IntegrityError):
            ProposalFactory(project=project, freelancer=freelancer)
    
    def test_duplicate_proposal_via_api_returns_400_not_500(self):
        project = OpenProjectFactory()
        freelancer = FreelancerFactory()
        ProposalFactory(project=project, freelancer=freelancer)

        api = APIClient()
        api.force_authenticate(user=freelancer)
        response = api.post(f"/api/v1/projects/{project.id}/proposals/", {
            "cover_letter": "Bidding on my own project",
            "bid_amount": "200.00",
        })
        assert response.status_code == 400