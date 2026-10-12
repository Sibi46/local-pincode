from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from jobs.models import State, District, PinCode
from newsdesk.models import NewsAgent


class NavigationPinTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='nav-admin', admin_role='super_admin')
        self.client.force_login(self.user)

    def test_state_district_and_all_registered_pins(self):
        state = State.objects.create(name='State one', code='S1')
        State.objects.create(name='Empty state', code='S2')
        district = District.objects.create(name='District one', state=state)
        for code in ('600001', '600002'):
            PinCode.objects.create(code=code, district=district)
        url = reverse('manage_pincodes')
        self.assertContains(self.client.get(url), 'Empty state')
        response = self.client.get(url, {'state_filter': state.pk, 'district_id': district.pk})
        self.assertContains(response, '600001')
        self.assertContains(response, '600002')
        self.assertEqual(response.context['selected'], district)

    def test_tuition_dashboard_omits_global_header(self):
        self.assertNotContains(self.client.get(reverse('tuition:dashboard')), 'class="navbar"')

    def test_post_news_button_requires_assignment(self):
        self.user.admin_role = ''
        self.user.save()
        url = reverse('newsdesk:feed')
        self.assertNotContains(self.client.get(url), '+ Post news')
        state = State.objects.create(name='Assigned state', code='AS')
        district = District.objects.create(name='Assigned district', state=state)
        pin = PinCode.objects.create(code='600003', district=district)
        NewsAgent.objects.create(user=self.user, pincode=pin, is_active=True)
        self.assertContains(self.client.get(url), '+ Post news')
