from django.urls import path
from .views import ContractDetailView, MarkDeliveredView, MarkCompletedView, RaiseDisputeView

urlpatterns = [
    path("contracts/<int:pk>/", ContractDetailView.as_view(), name="contract-detail"),
    path("contracts/<int:pk>/deliver/", MarkDeliveredView.as_view(), name="contract-deliver"),
    path("contracts/<int:pk>/complete/", MarkCompletedView.as_view(), name="contract-complete"),
    path("contracts/<int:pk>/dispute/", RaiseDisputeView.as_view(), name="contract-dispute"),
]