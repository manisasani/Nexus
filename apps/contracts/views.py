from rest_framework import generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from drf_spectacular.utils import extend_schema

from .models import Contract
from .serializers import ContractReadSerializer
from .services import ContractService


class ContractDetailView(generics.RetrieveAPIView):
    serializer_class = ContractReadSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Contract.objects.all()

    def get_object(self):
        contract = super().get_object()
        user = self.request.user
        if user.id not in (contract.client_id, contract.freelancer_id):
            raise PermissionDenied("You do not have access to this contract.")
        return contract


class ContractActionView(APIView):
    """
    Base view for contract state-transition actions.
    Subclasses set `service_method`.
    """
    permission_classes = [permissions.IsAuthenticated]
    service_method = None

    def post(self, request, pk):
        try:
            contract = self.service_method(contract_id=pk, actor=request.user)
        except Contract.DoesNotExist:
            raise NotFound("Contract not found.")
        except PermissionError as e:
            raise PermissionDenied(str(e))
        except DjangoValidationError as e:
            raise ValidationError(str(e))

        return Response(ContractReadSerializer(contract).data)


class MarkDeliveredView(ContractActionView):
    service_method = staticmethod(ContractService.mark_delivered)

    @extend_schema(
        summary="Mark contract as delivered",
        description="Only the freelancer on this contract can mark it as delivered. "
                    "Contract must currently be ACTIVE.",
        responses={200: ContractReadSerializer},
    )
    def post(self, request, pk):
        return super().post(request, pk)

class MarkCompletedView(ContractActionView):
    service_method = staticmethod(ContractService.mark_completed)

    @extend_schema(
        summary="Mark contract as delivered",
        description="Only the freelancer on this contract can mark it as delivered. "
                    "Contract must currently be ACTIVE.",
        responses={200: ContractReadSerializer},
    )
    def post(self, request, pk):
        return super().post(request, pk)


class RaiseDisputeView(ContractActionView):

    @extend_schema(
        summary="Raise a dispute on a contract",
        description="Either the client or freelancer can raise a dispute. "
                    "Contract must currently be DELIVERED.",
        responses={200: ContractReadSerializer},
    )
    def post(self, request, pk):
        note = request.data.get("note", "")
        try:
            contract = ContractService.raise_dispute(contract_id=pk, actor=request.user, note=note)
        except Contract.DoesNotExist:
            raise NotFound("Contract not found.")
        except PermissionError as e:
            raise PermissionDenied(str(e))
        except DjangoValidationError as e:
            raise ValidationError(str(e))
        return Response(ContractReadSerializer(contract).data)