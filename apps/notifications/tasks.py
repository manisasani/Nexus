import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, retry_backoff=True, retry_backoff_max=60)
def send_new_proposal_email(self, proposal_id):
    """
    Sends an email to the project owner when a new proposal is submitted.
    Takes an ID, not a model instance (Celery best practice).
    """
    from apps.projects.models import Proposal  

    try:
        proposal = Proposal.objects.select_related("project", "project__owner", "freelancer").get(
            id=proposal_id
        )
    except Proposal.DoesNotExist:
        logger.warning(f"send_new_proposal_email: Proposal {proposal_id} not found. Skipping.")
        return

    try:
        send_mail(
            subject=f"New proposal on '{proposal.project.title}'",
            message=(
                f"{proposal.freelancer.email} submitted a proposal of "
                f"${proposal.bid_amount} on your project '{proposal.project.title}'."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[proposal.project.owner.email],
        )
        logger.info(f"Sent new-proposal email for proposal {proposal_id}")
    except Exception as exc:
        logger.error(f"Failed to send new-proposal email for proposal {proposal_id}: {exc}")
        raise self.retry(exc=exc)