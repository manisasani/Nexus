from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Project
from .permissions import IsClient, IsOwner
from .serializers import (
    ProjectReadSerializer,
    ProjectCreateSerializer,
    ProjectUpdateSerializer,
)

class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

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
            raise ValidationError("Only projects in DRAFT status can be deleted.")
        instance.delete()