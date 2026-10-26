import math
import time
import logging
import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

_nominatim_last_call = 0   # enforce 1-req/sec for Nominatim ToS


def geocode_pincode(pincode: str) -> tuple[float | None, float | None]:
    """
    Return (latitude, longitude) for an Indian pincode.
    Tries Google Maps first (if GOOGLE_MAPS_KEY is set), then Nominatim.
    Results are cached for 30 days.
    """
    if not pincode or len(pincode) != 6 or not pincode.isdigit():
        return None, None

    cache_key = f"geocode_pin_{pincode}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    lat, lng = _geocode_google(pincode) or (None, None)
    if lat is None:
        lat, lng = _geocode_nominatim(pincode)

    if lat is not None:
        cache.set(cache_key, (lat, lng), timeout=60 * 60 * 24 * 30)

    return lat, lng


def _geocode_google(pincode: str) -> tuple[float, float] | None:
    key = getattr(settings, "GOOGLE_MAPS_KEY", "")
    if not key or key in ("YOUR_API_KEY", ""):
        return None
    try:
        resp = requests.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={"address": f"{pincode},India", "key": key},
            timeout=5,
        )
        data = resp.json()
        if data.get("status") == "OK":
            loc = data["results"][0]["geometry"]["location"]
            return float(loc["lat"]), float(loc["lng"])
    except Exception as e:
        logger.warning("Google geocode failed for %s: %s", pincode, e)
    return None


def _geocode_nominatim(pincode: str) -> tuple[float | None, float | None]:
    global _nominatim_last_call
    # Nominatim ToS: max 1 request/second
    gap = time.time() - _nominatim_last_call
    if gap < 1.1:
        time.sleep(1.1 - gap)
    _nominatim_last_call = time.time()

    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": f"{pincode}, India", "format": "json", "limit": 1,
                    "countrycodes": "in"},
            headers={"User-Agent": "PincodeJobPortal/1.0"},
            timeout=8,
        )
        results = resp.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
    except Exception as e:
        logger.warning("Nominatim geocode failed for %s: %s", pincode, e)
    return None, None


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Straight-line distance between two lat/lng points in kilometres."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def jobs_within_radius(lat: float, lng: float, radius_km: float = 5, queryset=None):
    """
    Return (job, distance_km) pairs for jobs within radius_km, sorted by distance.
    Uses a lat/lng bounding box in SQL for speed, then precise haversine in Python.
    """
    from .models import Job

    if queryset is None:
        queryset = Job.objects.filter(status="active")

    # 1° latitude ≈ 111 km
    lat_delta = radius_km / 111.0
    lng_delta = radius_km / (111.0 * math.cos(math.radians(lat)))

    nearby = queryset.filter(
        latitude__isnull=False,
        longitude__isnull=False,
        latitude__gte=lat - lat_delta,
        latitude__lte=lat + lat_delta,
        longitude__gte=lng - lng_delta,
        longitude__lte=lng + lng_delta,
    )

    results = []
    for job in nearby:
        dist = haversine_km(lat, lng, float(job.latitude), float(job.longitude))
        if dist <= radius_km:
            results.append((job, round(dist, 2)))

    results.sort(key=lambda x: x[1])
    return results


def generate_referral_code():
    """Generate a unique 8-character referral code."""
    import random
    import string
    from .models import User
    chars = string.ascii_uppercase + string.digits
    for _ in range(20):
        code = ''.join(random.choices(chars, k=8))
        if not User.objects.filter(referral_code=code).exists():
            return code
    return ''.join(random.choices(chars, k=12))


def ensure_referral_code(user):
    """Repair legacy accounts before displaying a share link, preserving existing codes."""
    from django.db import transaction
    from .models import User
    with transaction.atomic():
        locked = User.objects.select_for_update().get(pk=user.pk)
        if not locked.referral_code:
            locked.referral_code = generate_referral_code()
            locked.save(update_fields=['referral_code'])
        user.referral_code = locked.referral_code
    return user.referral_code


def generate_biz_id():
    """Generate a unique BIZXXXXXX salesman business ID (no hyphens)."""
    import random
    import string
    from .models import User
    digits = string.digits
    for _ in range(30):
        code = 'BIZ' + ''.join(random.choices(digits, k=6))
        if not User.objects.filter(salesman_biz_id=code).exists():
            return code
    return 'BIZ' + ''.join(random.choices(digits, k=8))


def award_referral_points(referrer, amount, txn_type, description):
    """Credit points to referrer's wallet and create a notification."""
    from .models import PointsWallet, PointsTransaction, UserNotification
    wallet, _ = PointsWallet.objects.get_or_create(user=referrer)
    wallet.balance += amount
    wallet.total_earned += amount
    wallet.save(update_fields=['balance', 'total_earned', 'updated_at'])
    PointsTransaction.objects.create(
        wallet=wallet,
        amount=amount,
        txn_type=txn_type,
        description=description,
    )
    UserNotification.objects.create(
        user=referrer,
        title=f'+{amount} Referral Points Earned!',
        message=description,
        notif_type='success',
        link='/referral/',
    )


def notify_seekers_for_job(job):
    """Create a UserNotification for every seeker whose profile matches this job."""
    from .models import User, UserNotification
    seekers = User.objects.filter(user_type='seeker').select_related('seeker')
    for seeker in seekers:
        try:
            sp = seeker.seeker
        except Exception:
            continue
        if sp.availability == 'not_looking':
            continue
        # Skip if collar preference doesn't match
        if sp.job_category and sp.job_category != 'any' and sp.job_category != job.collar_type:
            continue
        # Skip if both sides have an industry set but they don't overlap
        if sp.industry and job.industry:
            job_ind = job.industry.lower()
            seek_ind = sp.industry.lower()
            if job_ind not in seek_ind and seek_ind not in job_ind:
                continue
        UserNotification.objects.create(
            user=seeker,
            title=f'New Job: {job.title}',
            message=f'{job.title} in {job.location} is now hiring. Tap to apply!',
            notif_type='info',
            link=f'/jobs/{job.pk}/',
        )
