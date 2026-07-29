from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, retry_backoff=True)
def send_staff_reply_email(self, ticket_message_id):
    from .models import TicketMessage

    try:
        message = TicketMessage.objects.select_related("ticket", "ticket__opened_by").get(
            id=ticket_message_id
        )
    except TicketMessage.DoesNotExist:
        logger.warning(f"send_staff_reply_email: message {ticket_message_id} not found.")
        return

    try:
        send_mail(
            subject=f"Support replied to your ticket: {message.ticket.subject}",
            message=f"A support agent replied to your ticket #{message.ticket.id}:\n\n{message.body}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[message.ticket.opened_by.email],
        )
        logger.info(f"Sent staff-reply email for ticket message {ticket_message_id}")
    except Exception as exc:
        raise self.retry(exc=exc)