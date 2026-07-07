from django.urls import path

from apps.accounts.views import LogoutView, RegisterView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
]