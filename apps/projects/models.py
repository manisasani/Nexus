from django.db import models
from django.conf import settings

from django.core.exceptions import ValidationError
from datetime import date

from apps.accounts.models import CustomUser

class Project(models.Model):
    class Meta:
        ordering = ['-created_at']
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        OPEN = 'OPEN', 'Open'
        CLOSED = 'CLOSED', 'Closed'

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='owned_projects', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.title

def clean(self):
    if self.deadline and self.deadline < date.today():
        raise ValidationError("Deadline cannot be in the past.")


class Proposal(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'freelancer'],
                name='unique_proposal_per_project_per_freelancer'
            )
        ]
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        REJECTED = 'REJECTED', 'Rejected'

    project = models.ForeignKey(Project, related_name='proposals', on_delete=models.CASCADE)
    freelancer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='submitted_proposals', on_delete=models.CASCADE)
    cover_letter = models.TextField()
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        if self.bid_amount <= 0:
            raise ValidationError("Bid amount must be greater than zero.")
        if self.freelancer.role != CustomUser.Role.FREELANCER:
            raise ValidationError("Only users with the FREELANCER role can submit proposals.")
        if self.project.owner == self.freelancer:
            raise ValidationError("You cannot submit a proposal to your own project.")
        if self.project.status != Project.Status.OPEN:
            raise ValidationError("Proposals can only be submitted to projects that are OPEN.")
        
        
    def __str__(self):
        return f"Proposal by {self.freelancer.email} for {self.project.title}"