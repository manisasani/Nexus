from django.urls import path
from .views import MessageHistoryView, MarkMessagesReadView

urlpatterns = [
    path("chat/<int:room_id>/messages/", MessageHistoryView.as_view(), name="chat-history"),
    path("chat/<int:room_id>/mark-read/", MarkMessagesReadView.as_view(), name="chat-mark-read"),
]