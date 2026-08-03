from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.accounts.models import CustomUser
from apps.notifications.models import NotificationPreference
from apps.wallets.models import Wallet


@receiver(post_save, sender=CustomUser)
def create_wallet_for_new_user(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.get_or_create(user=instance)

@receiver(post_save, sender=CustomUser)
def create_notification_preference_for_new_user(sender, instance, created, **kwargs):
    if created:
        NotificationPreference.objects.get_or_create(user=instance)