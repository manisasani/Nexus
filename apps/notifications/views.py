from rest_framework import generics, permissions
from .models import Notification
from .serializers import NotificationsSerializer

class MyNotificationsView(generics.ListAPIView):
    serializer_class = NotificationsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)