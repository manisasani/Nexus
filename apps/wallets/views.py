import uuid
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import Wallet, LedgerEntry
from .services import WalletService
from .serializers import WalletSerializer, LedgerEntrySerializer


class AdminTopUpView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        user_id = request.data.get("user_id")
        amount = request.data.get("amount")
        idempotency_key = request.data.get("idempotency", str(uuid.uuid4()))

        wallet = generics.get_object_or_404(Wallet, user_id=user_id)

        try:
            entry = WalletService.credit(
                wallet_id=wallet.id,
                amount=int(amount),
                reference="Admin top-up (test/demo only)",
                idempotency_key=idempotency_key,
            )
        except DjangoValidationError as e:
            raise DRFValidationError(str(e))
        
        return Response(LedgerEntrySerializer(entry).data, status=201)
    

class MyWalletView(generics.RetrieveAPIView):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        wallet, _ = Wallet.objects.get_or_create(user=self.request.user)
        return wallet


class MyTransactionHistoryView(generics.ListAPIView):
    serializer_class = LedgerEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        wallet, _ = Wallet.objects.get_or_create(user=self.request.user)
        return LedgerEntry.objects.filter(wallet=wallet)