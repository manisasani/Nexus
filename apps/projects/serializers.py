from datetime import date

from rest_framework import serializers
from apps.projects.models import Project


class ProjectReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'title', 'description', 'budget', 'deadline', 'status', 'created_at', 'updated_at')

class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('title', 'description', 'budget', 'deadline')

    def validate_deadline(self, deadline):
        if deadline < date.today():
            raise serializers.ValidationError('Deadline cannot be in the past.')
        return deadline

    def validate_budget(self, budget):
        if budget <= 0:
            raise serializers.ValidationError('Budget must be greater than zero.')
        return budget

class ProjectUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('title', 'description', 'budget', 'deadline', 'status')
        read_only_fields = ('owner')

    def validate(self, data):
        current_status = self.instance.status
        new_status = data.get("status", current_status)

        allowed_transitions = {
            Project.Status.DRAFT: [Project.Status.DRAFT, Project.Status.OPEN],
            Project.Status.OPEN: [Project.Status.OPEN, Project.Status.CLOSED],
            Project.Status.CLOSED: [Project.Status.CLOSED],
        }

        if new_status not in allowed_transitions[current_status]:
            raise serializers.ValidationError(
                f"Cannot change status from {current_status} to {new_status}."
            )

        return data
    
    def validate_deadline(self, deadline):
        if deadline < date.today():
            raise serializers.ValidationError('Deadline cannot be in the past.')
        return deadline
    
    def validate_budget(self, budget):
        if budget <= 0:
            raise serializers.ValidationError('Budget must be greater than zero.')

    