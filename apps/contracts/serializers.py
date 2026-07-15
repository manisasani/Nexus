from rest_framework import serializers
from .models import Contract, ContractEvent


class ContractEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractEvent
        fields = ("id", "from_status", "to_status", "triggered_by", "note", "created_at")


class ContractReadSerializer(serializers.ModelSerializer):
    events = ContractEventSerializer(many=True, read_only=True)
    client_email = serializers.EmailField(source="client.email", read_only=True)
    freelancer_email = serializers.EmailField(source="freelancer.email", read_only=True)

    class Meta:
        model = Contract
        fields = (
            "id", "project", "proposal", "client", "client_email",
            "freelancer", "freelancer_email", "agreed_price", "status",
            "events", "created_at", "updated_at",
        )
        read_only_fields = fields