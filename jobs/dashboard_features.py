"""Registered employer services, using their existing approval state."""
from .models import Advertiser, CompanyProfile
from tuition.models import TeacherProfile
from vouchers.models import Business
from coupons.models import Shop


def registered_features(user):
    active, pending = [], []
    if not user.is_authenticated or not user.is_active:
        return active, pending
    def add(label, url, approved):
        (active if approved else pending).append({'label': label, 'url': url})
    if CompanyProfile.objects.filter(user=user).exclude(company_name='').exists():
        add('Business profile', '#my-profile', True)
    if Shop.objects.filter(business=user, is_active=True).exists():
        add('Coupons', '#coupons', True)
    for model, owner, label, url in [
        (Advertiser, 'user', 'Ads', '/advertise/dashboard/'),
        (Business, 'owner', 'Gift Vouchers', '/vouchers/dashboard/'),
        (TeacherProfile, 'owner', 'Tuition / Academy', '/tuition/learn/'),
    ]:
        statuses = set(model.objects.filter(**{owner: user}, status__in=['approved', 'pending']).values_list('status', flat=True))
        if statuses:
            add(label, url, 'approved' in statuses)
    return active, pending
