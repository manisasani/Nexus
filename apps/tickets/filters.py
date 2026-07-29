import django_filters
from .models import Ticket


class TicketFilter(django_filters.FilterSet):
    class Meta:
        model = Ticket
        fields = ["status", "category"]