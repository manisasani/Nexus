import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from redis import asyncio
from telegram import Bot
from django.utils import timezone
from datetime import timedelta

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

@shared_task(bind=True, max_retries=3, retry_backoff=True)
def send_proposal_accepted_email(self, contract_id):
    from apps.contracts.models import Contract

    try:
        contract = Contract.objects.select_related("freelancer", "project").get(id=contract_id)
    except Contract.DoesNotExist:
        logger.warning(f"send_proposal_accepted_email: Contract {contract_id} not found.")
        return

    try:
        send_mail(
            subject=f"Your proposal was accepted!",
            message=f"Your proposal on '{contract.project.title}' was accepted. Contract #{contract.id} is now active.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[contract.freelancer.email],
        )
        logger.info(f"Sent proposal-accepted email for contract {contract_id}")
    except Exception as exc:
        raise self.retry(exc=exc)

@shared_task(bind=True, max_retries=3, retry_backoff=True)
def send_contract_delivered_email(self, contract_id):
    from apps.contracts.models import Contract

    try:
        contract = Contract.objects.select_related("client", "project").get(id=contract_id)
    except Contract.DoesNotExist:
        logger.warning(f"send_contract_delivered_email: Contract {contract_id} not found.")
        return

    try:
        send_mail(
            subject=f"Work delivered on '{contract.project.title}'",
            message=f"The freelancer marked contract #{contract.id} as delivered. Please review and confirm completion.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[contract.client.email],
        )
        logger.info(f"Sent contract-delivered email for contract {contract_id}")
    except Exception as exc:
        raise self.retry(exc=exc)

@shared_task(bind=True, max_retries=3, retry_backoff=True)
def send_telegram_notification(self, user_id, message_text):
    from apps.accounts.models import CustomUser
    from .models import TelegramLink, NotificationPreference

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        logger.warning(f"send_telegram_notification: user {user_id} not found.")
        return

    try:
        pref = user.notification_preference
    except NotificationPreference.DoesNotExist:
        return

    if not pref.telegram_enabled:
        logger.info(f"Telegram notifications disabled for user {user_id}. Skipping.")
        return

    try:
        link = user.telegram_link
    except TelegramLink.DoesNotExist:
        logger.info(f"User {user_id} has telegram_enabled but no linked account. Skipping.")
        return

    try:
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        asyncio.run(bot.send_message(chat_id=link.chat_id, text=message_text))
        logger.info(f"Telegram message sent to user {user_id}")
    except Exception as exc:
        raise self.retry(exc=exc)

@shared_task
def send_weekly_digest():
    from .models import NotificationPreference, Notification

    one_week_ago = timezone.now() - timedelta(days=7)
    users_with_digest = NotificationPreference.objects.filter(digest_mode=True).select_related("user")

    for pref in users_with_digest:
        recent_notifications = Notification.objects.filter(
            recipient=pref.user, created_at__gte=one_week_ago
        )
        count = recent_notifications.count()
        if count == 0:
            continue

        summary_lines = [f"- {n.message}" for n in recent_notifications[:10]]
        summary_text = f"📊 Your weekly Nexus summary ({count} updates):\n\n" + "\n".join(summary_lines)

        if pref.telegram_enabled:
            send_telegram_notification.delay(pref.user.id, summary_text)

    logger.info(f"Weekly digest processed for {users_with_digest.count()} users with digest_mode enabled.")