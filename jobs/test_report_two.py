from django.contrib import messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase

from .models import Advertiser, CompanyProfile, Job, JobApplication, User
from .utils import ensure_referral_code
from .views import advertiser_dashboard


class ReportTwoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user('report-two-owner', user_type='company',
            city='Chennai', pincode='600001', address='Test address', salesman_biz_id='BIZTEST0001')
        cls.company = CompanyProfile.objects.create(user=cls.owner, company_name='Report Two Store',
            industry='Retail', company_size='1-10', website='https://example.com')
        cls.other = User.objects.create_user('report-two-other', user_type='company')
        cls.other_company = CompanyProfile.objects.create(user=cls.other, company_name='Other company')

    def setUp(self):
        self.client.force_login(self.owner)

    def test_dashboard_repairs_missing_referral_and_keeps_it_stable(self):
        session = self.client.session
        session['show_referral_popup'] = True
        session.save()
        response = self.client.get('/employer/dashboard/')
        self.owner.refresh_from_db()
        self.assertTrue(self.owner.referral_code)
        self.assertContains(response, f'value="http://testserver/register/?ref={self.owner.referral_code}"')
        self.assertEqual(ensure_referral_code(self.owner), self.owner.referral_code)
        self.assertEqual(self.client.get('/referral/').context['referral_link'], response.context['referral_link'])

    def test_existing_referral_is_preserved(self):
        self.owner.referral_code = 'KEEP1234'
        self.owner.save(update_fields=['referral_code'])
        self.assertEqual(ensure_referral_code(self.owner), 'KEEP1234')

    def test_published_job_redirects_to_real_pending_state(self):
        response = self.client.post('/post-job/', {'title': 'New vacancy', 'category': 'Sales',
            'collar_type': 'white', 'latitude': '13', 'longitude': '80', 'action': 'publish'})
        self.assertEqual(response.url, '/employer/dashboard/#approval-pending')
        job = Job.objects.get(posted_by=self.owner)
        self.assertFalse(job.is_approved)
        dashboard = self.client.get(response.url)
        self.assertEqual(list(dashboard.context['approval_pending']), [job])
        self.assertEqual(dashboard.context['active_jobs'].count(), 0)
        self.assertEqual(JobApplication.objects.count(), 0)
        self.assertContains(dashboard, 'Under review (1)')
        self.assertContains(dashboard, 'View submitted jobs')
        self.assertContains(dashboard, 'data-sec="approval-pending"', count=1)

    def test_draft_is_saved_and_visible_without_success_popup(self):
        response = self.client.post('/post-job/', {'title': 'Draft vacancy', 'action': 'draft',
            'latitude': '13', 'longitude': '80'})
        self.assertEqual(response.url, '/employer/dashboard/#pending-jobs')
        dashboard = self.client.get(response.url)
        self.assertEqual(dashboard.context['pending_jobs'].count(), 1)
        self.assertNotContains(dashboard, 'id="jobPostedOverlay"')

    def test_posting_page_identifies_company_and_compatible_map(self):
        response = self.client.get('/post-job/')
        self.assertContains(response, 'Posting for Report Two Store')
        self.assertContains(response, "referrerPolicy: 'strict-origin-when-cross-origin'")
        self.assertNotContains(response, '{s}.tile.openstreetmap.org')

    def test_advertiser_has_one_notification_bell(self):
        Advertiser.objects.create(user=self.owner, business_name='Report Two Store', status='pending')
        request = RequestFactory().get('/advertiser/dashboard/')
        request.user = self.owner
        request.session = self.client.session
        request._messages = FallbackStorage(request)
        messages.success(request, 'Your advertiser profile was saved.')
        response = advertiser_dashboard(request)
        self.assertEqual(response.content.count(b'aria-label="Notifications"'), 1)
        self.assertContains(response, 'Your advertiser profile was saved.')

    def test_business_description_is_owned_persistent_and_escaped(self):
        self.client.post('/employer/profile/save/', {'description': 'Local repairs\n<script>alert(1)</script>'})
        self.company.refresh_from_db()
        self.assertIn('Local repairs', self.company.description)
        self.other_company.refresh_from_db()
        self.assertEqual(self.other_company.description, '')
        public = self.client.get(f'/business/{self.company.company_id}/')
        self.assertContains(public, '&lt;script&gt;alert(1)&lt;/script&gt;')
        self.assertNotContains(public, '<script>alert(1)</script>')
        self.client.post('/employer/profile/save/', {'description': 'x' * 1001})
        self.company.refresh_from_db()
        self.assertIn('Local repairs', self.company.description)
        self.client.post('/employer/profile/save/', {'city': 'Chennai'})
        self.company.refresh_from_db()
        self.assertIn('Local repairs', self.company.description)

    def test_empty_company_description_has_clear_state(self):
        self.assertContains(self.client.get(f'/business/{self.company.company_id}/'),
            'This business has not added a description yet.')
