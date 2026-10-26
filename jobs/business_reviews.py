"""Customer reviews, owner-authorized rewards and monthly review snapshots."""
import secrets
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import BusinessReview, CompanyProfile, ReviewVoucher


def snapshot(reviews):
    stats = reviews.aggregate(count=Count('pk'), average=Avg('rating'))
    if not stats['count']:
        return 'No customer reviews yet.'
    positive = reviews.filter(rating__gte=4).count()
    critical = reviews.filter(rating__lte=2).count()
    return (f"{stats['count']} customer reviews; average {stats['average']:.1f}/5. "
            f"{positive} rated 4 or 5 stars; {critical} rated 1 or 2 stars.")


def badge(user):
    count = BusinessReview.objects.filter(user=user).count()
    return 'Community Expert' if count >= 10 else 'Local Guide' if count >= 3 else 'Community Reviewer'


@login_required
@require_POST
def submit_review(request, company_id):
    company = get_object_or_404(CompanyProfile, company_id=company_id, user__is_active=True)
    target = company.get_absolute_url() + '#customer-reviews'
    if company.user_id == request.user.pk:
        messages.error(request, 'You cannot review your own business.')
        return redirect(target)
    try:
        rating = int(request.POST.get('rating', ''))
    except (TypeError, ValueError):
        rating = 0
    text = request.POST.get('text', '').strip()
    if rating not in range(1, 6) or not 10 <= len(text) <= 2000:
        messages.error(request, 'Choose 1–5 stars and write a review of 10–2000 characters.')
        return redirect(target)
    with transaction.atomic():
        review, created = BusinessReview.objects.update_or_create(
            company=company, user=request.user, defaults={'rating': rating, 'text': text})
        if created and 1 <= company.review_reward_percent <= 50:
            ReviewVoucher.objects.create(
                review=review, code=secrets.token_hex(8).upper(),
                discount_percent=company.review_reward_percent,
                expires_at=timezone.now() + timedelta(days=30))
    messages.success(request, f'Review saved. Your badge: {badge(request.user)}. Rewards never depend on your rating.')
    return redirect(target)


@login_required
@require_POST
def redeem_review_voucher(request, company_id):
    company = get_object_or_404(CompanyProfile, company_id=company_id, user=request.user)
    updated = ReviewVoucher.objects.filter(
        review__company=company, code=request.POST.get('code', '').strip().upper(),
        redeemed_at__isnull=True, expires_at__gt=timezone.now()).update(redeemed_at=timezone.now())
    if updated:
        messages.success(request, 'Review voucher redeemed. Apply its discount to the customer’s purchase.')
    else:
        messages.error(request, 'Voucher is invalid, expired or already redeemed.')
    return redirect(company.get_absolute_url() + '#customer-reviews')
