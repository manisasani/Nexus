from django.db import models
from django.conf import settings
from apps.contracts.models import Contract


class Ticket(models.Model):
    class Category(models.TextChoices):
        GENERAL = "GENERAL", "General"
        PAYMENT = "PAYMENT", "Payment"
        DISPUTE = "DISPUTE", "Dispute"
        TECHNICAL = "TECHNICAL", "Technical"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        RESOLVED = "RESOLVED", "Resolved"
        CLOSED = "CLOSED", "Closed"

    subject = models.CharField(max_length=255)
    category = models.CharField(max_length=12, choices=Category.choices, default=Category.GENERAL)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.OPEN)
    opened_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="tickets", on_delete=models.PROTECT
    )
    contract = models.ForeignKey(
        Contract, related_name="tickets", on_delete=models.SET_NULL, null=True, blank=True
    )
    resolution = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Ticket #{self.id}: {self.subject} ({self.status})"

class TicketMessage(models.Model):
    ticket = models.ForeignKey(Ticket, related_name="messages", on_delete=models.CASCADE)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="ticket_messages", on_delete=models.SET_NULL, null=True
    )
    body = models.TextField()
    is_staff_reply = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message on Ticket #{self.ticket_id} by {self.author}"