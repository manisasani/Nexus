import pytest
from rest_framework.test import APIClient
from apps.accounts.factories import ClientFactory
from apps.accounts.models import CustomUser


@pytest.mark.django_db
class TestRegistration:
    def test_register_as_client_succeeds(self):
        client = APIClient()
        response = client.post("/api/v1/auth/register/", {
            "email": "newclient@example.com",
            "password": "StrongPass123!",
            "role": "CLIENT",
        })
        assert response.status_code == 201
        assert CustomUser.objects.filter(email="newclient@example.com").exists()

    def test_register_with_invalid_role_fails(self):
        client = APIClient()
        response = client.post("/api/v1/auth/register/", {
            "email": "hacker@example.com",
            "password": "StrongPass123!",
            "role": "ADMIN",
        })
        assert response.status_code == 400
        assert not CustomUser.objects.filter(email="hacker@example.com").exists()


@pytest.mark.django_db
class TestLogin:
    def test_login_with_correct_credentials_returns_tokens(self):
        user = ClientFactory(password="correctpass")
        client = APIClient()
        response = client.post("/api/v1/auth/login/", {
            "email": user.email,
            "password": "correctpass",
        })
        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_with_wrong_password_fails(self):
        user = ClientFactory(password="correctpass")
        client = APIClient()
        response = client.post("/api/v1/auth/login/", {
            "email": user.email,
            "password": "wrongpass",
        })
        assert response.status_code == 401


@pytest.mark.django_db
class TestMeEndpoint:
    def test_authenticated_user_can_view_own_profile(self):
        user = ClientFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get("/api/v1/auth/me/")
        assert response.status_code == 200
        assert response.data["email"] == user.email

    def test_unauthenticated_request_returns_401(self):
        client = APIClient()
        response = client.get("/api/v1/auth/me/")
        assert response.status_code == 401

    def test_user_cannot_change_own_role_via_patch(self):
        user = ClientFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.patch("/api/v1/auth/me/", {"role": "FREELANCER"})
        user.refresh_from_db()
        assert user.role == CustomUser.Role.CLIENT  