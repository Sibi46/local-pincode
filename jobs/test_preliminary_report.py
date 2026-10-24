from datetime import timedelta
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from .models import Job, User


class PreliminaryReportTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user('review-employer', user_type='company')
        cls.member = User.objects.create_user('review-member', password='Example-pass-123')
        cls.admin = User.objects.create_user('review-admin', admin_role='super_admin')
        today = timezone.localdate()
        cls.live = Job.objects.create(posted_by=cls.owner, title='Current vacancy',
            is_approved=True, job_plan='free', last_date=today, plan_expires_at=today,
            latitude=13, longitude=80, pincode='600001')
        cls.hidden = []
        for extra in ({'last_date': today - timedelta(days=1)},
                      {'plan_expires_at': today - timedelta(days=1)},
                      {'is_approved': False}, {'status': 'closed'},
                      {'job_plan': 'paid_pending'}):
            fields = dict(posted_by=cls.owner, title='Unavailable vacancy',
                is_approved=True, job_plan='free', latitude=13, longitude=80, pincode='600001')
            fields.update(extra)
            cls.hidden.append(Job.objects.create(**fields))

    def setUp(self):
        cache.clear()

    def test_home_has_no_public_admin_panel(self):
        for user in (None, self.member):
            if user:
                self.client.force_login(user)
            response = self.client.get('/')
            self.assertNotContains(response, 'id="adminModal"')
            self.assertNotContains(response, 'Admin Control Panel')
            self.assertNotContains(response, 'aria-label="Admin workspace"')
        self.client.force_login(self.admin)
        self.assertContains(self.client.get('/'), 'aria-label="Admin workspace"')

    def test_nonadmins_cannot_read_or_write_admin_routes(self):
        for user in (None, self.member):
            if user:
                self.client.force_login(user)
            for url in ('/super-admin/', '/admin/', '/admin-workspace/', '/admin-panel/ads/'):
                for method in (self.client.get, self.client.post):
                    response = method(url)
                    self.assertIn(response.status_code, (302, 403, 404))
        self.assertFalse(self.client.post('/admin-panel/login/',
            {'phone': self.member.username, 'password': 'Example-pass-123'}).wsgi_request.user.admin_role)

    def test_discovery_and_detail_exclude_unavailable_jobs(self):
        response = self.client.get('/jobs/')
        self.assertEqual(list(response.context['jobs']), [self.live])
        home = self.client.get('/')
        self.assertEqual(list(home.context['featured_jobs']), [self.live])
        self.assertEqual(self.client.get(f'/jobs/{self.live.pk}/').status_code, 200)
        self.client.force_login(self.member)
        for job in self.hidden:
            self.assertEqual(self.client.get(f'/jobs/{job.pk}/').status_code, 404)
            self.assertEqual(self.client.post(f'/jobs/{job.pk}/apply/').status_code, 404)

    def test_search_handles_empty_results_and_invalid_radius(self):
        self.assertEqual(self.client.get('/jobs/?q=nonexistentxyz').context['total'], 0)
        with patch('jobs.utils.geocode_pincode') as geocode:
            for value in ('oops', 'nan', 'inf', '-1', '0', '501'):
                response = self.client.get('/jobs/', {'pincode': '600001', 'radius': value})
                self.assertTrue(response.context['radius_error'])
                response = self.client.get('/api/nearby-jobs/', {'pincode': '600001', 'radius': value})
                self.assertEqual(response.status_code, 400)
            geocode.assert_not_called()

    def test_nearby_api_obeys_publication_rules(self):
        with patch('jobs.utils.geocode_pincode', return_value=(13, 80)):
            response = self.client.get('/api/nearby-jobs/?pincode=600001&radius=5')
        self.assertEqual(response.status_code, 200)
        self.assertEqual([job['id'] for job in response.json()['jobs']], [self.live.pk])

    def test_malformed_auth_requests_are_validation_errors(self):
        for url in ('/api/verify-otp/', '/api/check-phone/'):
            for body in ('{', '[]', 'null', '{"phone": null, "otp": null}'):
                response = self.client.post(url, body, content_type='application/json')
                self.assertLess(response.status_code, 500)
        self.assertFalse(self.client.post('/api/send-otp/', {'phone': 'invalid'}).json()['success'])
