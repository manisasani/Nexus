from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .services.telegram_link_service import TelegramLinkService

from .models import Notification
from .serializers import NotificationsSerializer

class MyNotificationsView(generics.ListAPIView):
    serializer_class = NotificationsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

class GenerateTelegramLinkCodeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        code = TelegramLinkService.generate_link_code(request.user)
        return Response({
            "code": code,
            "instructions": "Send this code to the Nexus Telegram bot within 10 minutes.",
        }, status=status.HTTP_200_OK)