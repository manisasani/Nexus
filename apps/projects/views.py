from django.db import IntegrityError
from xml.dom import ValidationErr

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from .models import Project, Proposal
from .permissions import IsClient, IsFreelancer, IsOwner, IsProposalOwnerPending
from .filters import ProjectFilter
from .serializers import (
    ProjectReadSerializer,
    ProjectCreateSerializer,
    ProjectUpdateSerializer,
    ProposalCreateSerializer,
    ProposalReadSerializer,
    ProposalStatusUpdateSerializer,
    ProposalUpdateSerializer,
)

class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProjectFilter

    def get_permissions(self):
        if self.action == "create":
            return [permissions.IsAuthenticated(), IsClient()]
        if self.action in ["update", "partial_update", "destroy", "retrieve"]:
            return [permissions.IsAuthenticated(), IsOwner()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return ProjectCreateSerializer
        if self.action in ["update", "partial_update"]:
            return ProjectUpdateSerializer
        return ProjectReadSerializer
    
    def get_queryset(self):
        user = self.request.user
        qs = Project.objects.all()

        if self.action == "list":
            return qs.filter(status=Project.Status.OPEN)
        
        return qs

    @action(detail=True, methods=["get"], url_path="mine")
    def mine(self, request):
        qs = Project.objects.filter(owner=request.user)
        page = self.paginate_queryset(qs)
        serializer = ProjectReadSerializer(page or qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        if instance.status != Project.Status.DRAFT:
            from rest_framework.exceptions import ValidationError
            raise ValidationError('Only projects in DRAFT status can be deleted.')
        instance.delete()


class ProposalViewSet(viewsets.ModelViewSet):

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated(), IsFreelancer()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsProposalOwnerPending()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        project = get_object_or_404(Project, id=self.kwargs["project_id"])
        user = self.request.user

        if project.owner_id == user.id:
            return Proposal.objects.filter(project=project)

        return Proposal.objects.filter(project=project, freelancer=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return ProposalCreateSerializer
        if self.action in ['update', 'partial_update']:
            return ProposalUpdateSerializer
        return ProposalReadSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["project"] = get_object_or_404(Project, id=self.kwargs["project_id"])
        return context

    def perform_create(self, serializer):
        project = get_object_or_404(Project, id=self.kwargs["project_id"])
        try:
            serializer.save(project=project, freelancer=self.request.user)
        except IntegrityError:
            raise ValidationError(
                {"detail": "You already submitted a proposal on this project."}
            )


    @action(detail=True, methods=["post"], url_path="accept")
    def accept(self, request, project_id=None, pk=None):
        proposal = self.get_object_for_status_change(request, pk)
        serializer = ProposalStatusUpdateSerializer(
            data={"status": "ACCEPTED"},
            context={"proposal": proposal},
        )
        serializer.is_valid(raise_exception=True)
        proposal.status = Proposal.Status.ACCEPTED
        proposal.save(update_fields=["status"])
        return Response(ProposalReadSerializer(proposal).data)


    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, project_id=None, pk=None):
        proposal = self.get_object_for_status_change(request, pk)
        serializer = ProposalStatusUpdateSerializer(
            data={"status": "REJECTED"},
            context={"proposal": proposal},
        )
        serializer.is_valid(raise_exception=True)
        proposal.status = Proposal.Status.REJECTED
        proposal.save(update_fields=["status"])
        return Response(ProposalReadSerializer(proposal).data)

    def get_object_for_status_change(self, request, pk):
        project = get_object_or_404(Project, id=self.kwargs["project_id"])
        proposal = get_object_or_404(Proposal, id=pk, project=project)

        
        if project.owner_id != request.user.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only the project owner can accept or reject proposals.")

        return proposal