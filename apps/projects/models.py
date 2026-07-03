from django.db import models
from django.conf import settings

from django.core.exceptions import ValidationError
from datetime import date

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
