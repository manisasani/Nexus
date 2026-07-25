import pytest
from django.core import mail
from rest_framework.test import APIClient
from apps.projects.factories import OpenProjectFactory
from apps.accounts.factories import FreelancerFactory
from apps.notifications.models import Notification


@pytest.mark.django_db
class TestProposalCreationTriggersNotifications:
    def test_creating_proposal_sends_email_and_notification(self):
        project = OpenProjectFactory()
        freelancer = FreelancerFactory()

        api = APIClient()
        api.force_authenticate(user=freelancer)
        response = api.post(f"/api/v1/projects/{project.id}/proposals/", {
            "cover_letter": "Testing Celery notifications",
            "bid_amount": "300.00",
        })

        assert response.status_code == 201

        assert Notification.objects.filter(
            recipient=project.owner,
            notification_type=Notification.NotificationType.NEW_PROPOSAL,
        ).exists()

        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [project.owner.email]