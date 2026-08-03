from celery import shared_task
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)


@shared_task
def purge_expired_otps():
    
    logger.info("purge_expired_otps: Redis TTL handles expiry automatically. No-op.")