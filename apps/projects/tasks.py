from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def close_stale_open_projects():
    """
    Closes OPEN projects that have had no activity (no new proposals)
    for more than 30 days.
    """
    from apps.projects.models import Project

    cutoff = timezone.now() - timedelta(days=30)
    stale_projects = Project.objects.filter(
        status=Project.Status.OPEN,
        created_at__lt=cutoff,
    )
    count = stale_projects.update(status=Project.Status.CLOSED)
    logger.info(f"close_stale_open_projects: closed {count} stale projects.")
    return count