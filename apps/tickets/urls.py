from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import TicketViewSet, TicketMessageCreateView

router = DefaultRouter()
router.register(r"tickets", TicketViewSet, basename="ticket")

urlpatterns = router.urls + [
    path("tickets/<int:ticket_id>/messages/", TicketMessageCreateView.as_view(), name="ticket-messages"),
]