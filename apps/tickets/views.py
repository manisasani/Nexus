from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied, NotFound
from django.db import transaction

from apps.tickets.filters import TicketFilter
from .tasks import send_staff_reply_email

from .models import Ticket, TicketMessage
from .permissions import IsStaffUser, IsTicketOwnerOrStaff
from .serializers import (
    TicketCreateSerializer,
    TicketMessageSerializer,
    TicketReadSerializer,
    TicketMessageCreateSerializer,
    TicketStaffUpdateSerializer,
)


class TicketViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_class = TicketFilter

    def get_permissions(self):
        if self.action in ["update", "partial_update"]:
            return [permissions.IsAuthenticated(), IsStaffUser()]
        if self.action in ["retrieve", "destroy"]:
            return [permissions.IsAuthenticated(), IsTicketOwnerOrStaff()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return TicketCreateSerializer
        if self.action in ["update", "partial_update"]:
            return TicketStaffUpdateSerializer
        return TicketReadSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Ticket.objects.select_related("opened_by", "contract").prefetch_related("messages")

        if user.is_staff:
            return qs  

        return qs.filter(opened_by=user) 

    def perform_create(self, serializer):
        serializer.save(opened_by=self.request.user)

    @action(detail=False, methods=["get"], url_path="mine")
    def mine(self, request):
        qs = Ticket.objects.filter(opened_by=request.user)
        page = self.paginate_queryset(qs)
        serializer = TicketReadSerializer(page or qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

class TicketMessageCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, ticket_id):
        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            raise NotFound("Ticket not found.")

        user = request.user
        if not user.is_staff and ticket.opened_by_id != user.id:
            raise PermissionDenied("You do not have access to this ticket.")

        serializer = TicketMessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = TicketMessage.objects.create(
            ticket=ticket,
            author=user,
            body=serializer.validated_data["body"],
            is_staff_reply=user.is_staff,
        )

        if message.is_staff_reply:
            transaction.on_commit(
                lambda: send_staff_reply_email.delay(message.id)
            )

        return Response(
            TicketMessageSerializer(message).data,
            status=status.HTTP_201_CREATED,
        )