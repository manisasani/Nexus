import django_filters
from .models import Project

class ProjectFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(
        field_name='status',
        lookup_expr='exact',
    )

    budget_min = django_filters.NumberFilter(
        field_name='budget',
        lookup_expr='gte',
    )

    budget_max = django_filters.NumberFilter(
        field_name='budget',
        lookup_expr='lte',
    )

    class Meta:
        model = Project
        fields = ['status', 'budget_min', 'budget_max']