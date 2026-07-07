from django.urls import path

from apps.accounts.views import RegisterView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
]