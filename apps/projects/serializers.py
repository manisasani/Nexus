from datetime import date
from django.db import IntegrityError

from rest_framework import serializers
from apps.projects.models import Project, Proposal


class ProjectReadSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source="owner.email", read_only=True)

    class Meta:
        model = Project
        fields = ('id', 'title', 'description', 'budget', 'deadline', 'status',
                  'owner', 'owner_email', 'created_at', 'updated_at')
        read_only_fields = ('owner',)

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
        fields = ('title', 'owner', 'description', 'budget', 'deadline', 'status')
        read_only_fields = ('owner',)

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
        return budget

    
class ProposalReadSerializer(serializers.ModelSerializer):
    freelancer_email = serializers.EmailField(
        source="freelancer.email",
        read_only=True
    )
    class Meta:
        model = Proposal
        fields = ('id', 'project', 'freelancer', 'freelancer_email',
                  'bid_amount', 'cover_letter', 'status', 'created_at', 'updated_at')
        read_only_fields = ('freelancer', 'status')


class ProposalCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = ('bid_amount', 'cover_letter')
    
    def validate_bid_amount(self, bid_amount):
        if bid_amount <= 0:
            raise serializers.ValidationError('Bid amount must be greater than zero.')
        return bid_amount
    
    def validate(self, data):
        request = self.context['request']
        project = self.context['project']
        user = request.user

        if user.role != 'FREELANCER':
            raise serializers.ValidationError('Only freelancer can submit proposals.')
        
        if project.status != Project.Status.OPEN:
            raise serializers.ValidationError('You can only apply to OPEN projects.')
        
        if project.owner_id == user.id:
            raise serializers.ValidationError('You cannot submit a proposal to you own project.')
        
        return data

    
    def create(self, validated_data):
        request = self.context['request']
        project = self.context['project']

        try:
            return Proposal.objects.create(
                project=project,
                freelancer=request.user,
                **validated_data
            )
        except IntegrityError:
            raise serializers.ValidationError(
                'You have already a proposal for ths project.'
            )

class ProposalUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = ('bid_amount', 'cover_letter')
    
    def validate(self, attrs):
        if self.instance and self.instance.status != Proposal.Status.PENDING:
            raise serializers.ValidationError(
                {"detail": "Only pending proposals can be edited."}
            )
        return attrs
    
    def validate_bid_amount(self, bid_amount):
        if bid_amount <= 0:
            raise serializers.ValidationError('Bid amount must be greater than zero.')
        return bid_amount

class ProposalStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["ACCEPTED", "REJECTED"])

    def validate_status(self, value):
        proposal = self.context["proposal"]
        if proposal.status != Proposal.Status.PENDING:
            raise serializers.ValidationError(
                "Only pending proposals can be accepted or rejected."
            )
        return value