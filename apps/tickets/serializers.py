from rest_framework import serializers
from .models import Ticket, TicketMessage


class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("subject", "category", "contract")

    def validate_contract(self, contract):
        if contract is None:
            return contract
        request = self.context["request"]
        user = request.user
        if user.id not in (contract.client_id, contract.freelancer_id):
            raise serializers.ValidationError(
                "You can only link a ticket to your own contract."
            )
        return contract

class TicketMessageSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source="author.email", read_only=True)

    class Meta:
        model = TicketMessage
        fields = ("id", "author", "author_email", "body", "is_staff_reply", "created_at")
        read_only_fields = fields


class TicketReadSerializer(serializers.ModelSerializer):
    messages = TicketMessageSerializer(many=True, read_only=True)
    opened_by_email = serializers.EmailField(source="opened_by.email", read_only=True)

    class Meta:
        model = Ticket
        fields = (
            "id", "subject", "category", "status", "opened_by", "opened_by_email",
            "contract", "resolution", "messages", "created_at", "updated_at",
        )
        read_only_fields = fields

class TicketMessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketMessage
        fields = ("body",)

class TicketStaffUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("status", "resolution")

    def validate(self, attrs):
        new_status = attrs.get("status")
        if new_status in (Ticket.Status.RESOLVED, Ticket.Status.CLOSED):
            resolution = attrs.get("resolution") or self.instance.resolution
            if not resolution:
                raise serializers.ValidationError(
                    "A resolution note is required to resolve or close a ticket."
                )
        return attrs


