"""Consistent publication rules for job discovery and applications."""
from django.db.models import Q
from django.utils import timezone

from .models import Job, User


def public_jobs():
    today = timezone.localdate()
    return Job.objects.filter(
        status='active', is_approved=True, job_plan__in=['free', 'paid'],
        posted_by__is_active=True, posted_by__user_type__in=User.EMPLOYER_TYPES,
    ).filter(
        Q(last_date__isnull=True) | Q(last_date__gte=today),
    ).filter(
        Q(plan_expires_at__isnull=True) | Q(plan_expires_at__gte=today),
    )
