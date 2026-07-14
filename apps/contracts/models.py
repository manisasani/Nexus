from django.db import models
from django.conf import settings
from apps.projects.models import Project, Proposal

class Contract(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        DELIVERED = "DELIVERED", "Delivered"
        COMPLETED = "COMPLETED", "Completed"
        DISPUTED = "DISPUTED", "Disputed"
        CANCELLED = "CANCELLED", "Cancelled"

    project = models.OneToOneField(
        Project, related_name="contract", on_delete=models.PROTECT
    )
    proposal = models.OneToOneField(
        Proposal, related_name="contract", on_delete=models.PROTECT
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="client_contracts", on_delete=models.PROTECT
    )
    freelancer = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="freelancer_contracts", on_delete=models.PROTECT
    )
    agreed_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Contract for {self.project.title} ({self.status})"

class ContractEvent(models.Model):
    contract = models.ForeignKey(Contract, related_name="events", on_delete=models.CASCADE)
    from_status = models.CharField(max_length=12, blank=True)
    to_status = models.CharField(max_length=12)
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="contract_events", on_delete=models.SET_NULL, null=True
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.contract_id}: {self.from_status} -> {self.to_status}"
    