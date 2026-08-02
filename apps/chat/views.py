from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied, NotFound
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import ChatRoom, Message
from .serializers import MessageSerializer


class MessageHistoryView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        room_id = self.kwargs["room_id"]
        try:
            room = ChatRoom.objects.get(id=room_id)
        except ChatRoom.DoesNotExist:
            raise NotFound("Chat room not found.")

        if not room.is_participant(self.request.user):
            raise PermissionDenied("You are not a participant in this chat.")

        return Message.objects.filter(room=room).select_related("sender")

class MarkMessagesReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, room_id):
        try:
            room = ChatRoom.objects.get(id=room_id)
        except ChatRoom.DoesNotExist:
            raise NotFound("Chat room not found.")

        if not room.is_participant(request.user):
            raise PermissionDenied("You are not a participant in this chat.")

        updated = Message.objects.filter(
            room=room, read_at__isnull=True
        ).exclude(sender=request.user).update(read_at=timezone.now())

        return Response({"marked_read": updated}, status=status.HTTP_200_OK)