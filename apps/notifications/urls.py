from django.urls import path
from .views import GenerateTelegramLinkCodeView, MyNotificationPreferenceView, MyNotificationsView

urlpatterns = [
    path("notifications/", MyNotificationsView.as_view(), name="my-notifications"),
    path("notifications/preferences/", MyNotificationPreferenceView.as_view(), name="notification-preferences"),
    path("notifications/telegram/link-code/", GenerateTelegramLinkCodeView.as_view(), name="telegram-link-code"),
]