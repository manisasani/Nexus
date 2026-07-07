from django.urls import path

from apps.accounts.views import LogoutView, RegisterView

from .views import RegisterView, LogoutView, ThrottledTokenObtainPairView, MeView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", ThrottledTokenObtainPairView.as_view(), name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/me/", MeView.as_view(), name="me"),
]