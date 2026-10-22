"""Public feature destinations used by homepage discovery and search."""
FEATURES = [
    {'name': 'Shops and businesses', 'url': '/businesses/', 'keywords': 'store shopping local company directory'},
    {'name': 'Offers', 'url': '/advertise/', 'keywords': 'deals discounts sale advertisement'},
    {'name': 'Community', 'url': '/portal/', 'keywords': 'communities neighbours groups participate'},
    {'name': 'Family', 'url': '/community/family/', 'keywords': 'relatives family tree'},
    {'name': 'Jobs', 'url': '/jobs/', 'keywords': 'work employment career vacancy hiring'},
    {'name': 'My Ask', 'url': '/network/', 'keywords': 'network questions help neighbours'},
    {'name': 'News Desk', 'url': '/news/', 'keywords': 'news local updates headlines'},
    {'name': 'Flicks', 'url': '/flicks/', 'keywords': 'video reels films watch'},
    {'name': 'Quiz', 'url': '/quiz/play/', 'keywords': 'questions knowledge trivia play'},
    {'name': 'Advertise your business', 'url': '/advertise/register/', 'keywords': 'promote marketing ads campaign'},
    {'name': 'Tuitions', 'url': '/tuition/', 'keywords': 'teacher tutor academy classes learning education'},
    {'name': 'School Corner', 'url': '/community/school-corner/', 'keywords': 'school students children education'},
    {'name': 'Campus', 'url': '/campus/', 'keywords': 'college university student placement'},
    {'name': 'Health', 'url': '/health/', 'keywords': 'doctor care hospital wellness'},
    {'name': 'Coupons', 'url': '/coupons/activate/', 'keywords': 'gift points activate reward'},
    {'name': 'Events', 'url': '/portal/events/', 'keywords': 'activities meetup calendar'},
    {'name': 'Gift Vouchers', 'url': '/vouchers/marketplace/', 'keywords': 'voucher gifts coupon shopping'},
    {'name': 'Messages', 'url': '/messages/', 'keywords': 'chat conversations inbox'},
    {'name': 'Register Business', 'url': '/register/?type=company', 'keywords': 'join company shop registration'},
    {'name': 'My Profile', 'url': '/profile/edit/', 'keywords': 'account photo personal settings'},
]


def search_features(query):
    words = query.casefold().split()
    return [item for item in FEATURES if all(
        word in (item['name'] + ' ' + item['keywords']).casefold() for word in words
    )] if words else []
