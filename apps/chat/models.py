from django.db import models
from django.conf import settings
from apps.contracts.models import Contract


class ChatRoom(models.Model):
    contract = models.OneToOneField(
        Contract, related_name="chat_room", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ChatRoom for Contract #{self.contract_id}"

    def is_participant(self, user):
        return user.id in (self.contract.client_id, self.contract.freelancer_id)

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="chat_messages", on_delete=models.SET_NULL, null=True
    )
    content = models.TextField()
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message from {self.sender} at {self.created_at}"