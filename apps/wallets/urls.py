from django.urls import path
from .views import AdminTopUpView, MyWalletView, MyTransactionHistoryView

urlpatterns = [
    path("wallet/", MyWalletView.as_view(), name="my-wallet"),
    path("wallet/transactions/", MyTransactionHistoryView.as_view(), name="my-transactions"),
    path("wallet/admin-topup/", AdminTopUpView.as_view(), name="admin-topup"),
]