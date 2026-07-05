from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ProjectViewSet, ProposalViewSet

router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="project")

proposal_list = ProposalViewSet.as_view({
    "get": "list",
    "post": "create",
})
proposal_detail = ProposalViewSet.as_view({
    "get": "retrieve",
    "patch": "partial_update",
    "put": "update",
    "delete": "destroy",
})

proposal_accept = ProposalViewSet.as_view({"post": "accept"})
proposal_reject = ProposalViewSet.as_view({"post": "reject"})

urlpatterns = router.urls + [
    path("projects/<int:project_id>/proposals/", proposal_list, name="project-proposals-list"),
    path("projects/<int:project_id>/proposals/<int:pk>/", proposal_detail, name="project-proposals-detail"),
    path("projects/<int:project_id>/proposals/<int:pk>/accept/", proposal_accept, name="project-proposal-accept"),
    path("projects/<int:project_id>/proposals/<int:pk>/reject/", proposal_reject, name="project-proposal-reject"),
]