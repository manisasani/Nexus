import pytest
from django.core import mail
from apps.projects.factories import OpenProjectFactory, ProposalFactory
from apps.notifications.tasks import send_new_proposal_email
from apps.notifications.models import Notification


@pytest.mark.django_db
class TestNewProposalEmailTask:
    def test_sends_email_to_project_owner(self):
        project = OpenProjectFactory()
        proposal = ProposalFactory(project=project)

        send_new_proposal_email(proposal.id) 

        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [project.owner.email]
        assert project.title in mail.outbox[0].subject

    def test_missing_proposal_does_not_crash(self):
        send_new_proposal_email(99999)
        assert len(mail.outbox) == 0