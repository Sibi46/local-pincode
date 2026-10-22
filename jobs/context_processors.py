from django.utils import timezone
from .models import Advertisement


def site_ads(request):
    from .features import FEATURES, search_features
    photo_url = ''
    if request.user.is_authenticated:
        seeker = getattr(request.user, 'seeker', None)
        company = getattr(request.user, 'company', None)
        photo = getattr(seeker, 'photo', None) or getattr(company, 'logo', None)
        if photo:
            photo_url = photo.url
    today = timezone.now().date()
    ads = (Advertisement.objects
           .filter(status='active', start_date__lte=today, end_date__gte=today)
           .exclude(image='')
           .select_related('advertiser', 'package')[:30])

    by_type = {}
    for ad in ads:
        t = ad.package.ad_type
        by_type.setdefault(t, []).append(ad)

    pending_ad_posts = 0
    if request.user.is_authenticated and getattr(request.user, 'admin_role', '') == 'super_admin':
        from .models import AdPost
        pending_ad_posts = AdPost.objects.filter(status='pending').count()

    return {
        'site_ads': ads,
        'profile_photo_url': photo_url,
        'ads_by_type': by_type,
        'pending_ad_posts': pending_ad_posts,
        'feature_catalog': FEATURES if request.path == '/' else [],
        'feature_query': request.GET.get('feature', '').strip() if request.path == '/' else '',
        'feature_matches': search_features(request.GET.get('feature', '')) if request.path == '/' else [],
    }
