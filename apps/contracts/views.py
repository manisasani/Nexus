from rest_framework import generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound

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


class MarkCompletedView(ContractActionView):
    service_method = staticmethod(ContractService.mark_completed)


class RaiseDisputeView(ContractActionView):
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