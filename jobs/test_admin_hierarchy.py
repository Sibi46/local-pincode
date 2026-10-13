from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from .models import User, Country, State, District, PinCode, AdminProfile
from .admin_hierarchy import authority, AssignmentForm, visible_team


class HierarchyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root = User.objects.create_user('rootadmin', admin_role='super_admin')
        cls.country = Country.objects.create(name='India', code='IN')
        cls.state = State.objects.create(name='Tamil Nadu', code='TN', country=cls.country)
        cls.other = State.objects.create(name='Delhi', code='DL', country=cls.country)
        cls.district = District.objects.create(name='Chennai', state=cls.state)
        cls.area = PinCode.objects.create(code='600001', district=cls.district)
        cls.chain = []
        parent = cls.root
        for level in ['country', 'state', 'district', 'area', 'salesman']:
            user = User.objects.create_user(level, admin_role='scoped_admin')
            p = AdminProfile.objects.create(user=user, role='scoped_admin', hierarchy_level=level,
                appointed_by=parent, country=cls.country,
                state=cls.state if level != 'country' else None,
                district=cls.district if level in ['district', 'area', 'salesman'] else None,
                area=cls.area if level in ['area', 'salesman'] else None)
            cls.chain.append(p)
            parent = user

    def test_chain_scope_and_render(self):
        for index, p in enumerate(self.chain):
            self.assertEqual(authority(p.user).pk, p.pk)
            self.assertEqual(visible_team(p.user).count(), 4-index)
            self.client.force_login(p.user)
            self.assertEqual(self.client.get(reverse('hierarchy_workspace')).status_code, 200)
        self.client.force_login(self.root)
        self.assertContains(self.client.get(reverse('hierarchy_workspace')), 'Create Country Admin')

    def test_parent_suspension_blocks_descendants(self):
        AdminProfile.objects.filter(pk=self.chain[0].pk).update(is_active=False)
        for p in self.chain:
            with self.assertRaises(PermissionDenied): authority(p.user)

    def test_wrong_parent_role_denied(self):
        User.objects.filter(pk=self.chain[0].user_id).update(admin_role='')
        with self.assertRaises(PermissionDenied): authority(self.chain[-1].user)

    def test_next_level_and_cross_state(self):
        state_admin = self.chain[1].user
        data = {'level': 'district', 'district': self.district.pk}
        self.assertTrue(AssignmentForm(data, actor=state_admin).is_valid())
        data['level'] = 'country'
        self.assertFalse(AssignmentForm(data, actor=state_admin).is_valid())
        other_district = District.objects.create(name='Other', state=self.other)
        data.update(level='district', district=other_district.pk)
        self.assertFalse(AssignmentForm(data, actor=state_admin).is_valid())

    def test_no_legacy_content_bypass(self):
        self.client.force_login(self.chain[1].user)
        self.assertEqual(self.client.post('/super-admin/team/').status_code, 403)
        self.assertEqual(self.client.post(reverse('assigned_action', args=['jobs', 1])).status_code, 403)
        self.assertEqual(self.client.post(reverse('hierarchy_geography')).status_code, 403)

    def test_create_salesman_and_no_staff(self):
        self.client.force_login(self.chain[3].user)
        response = self.client.post(reverse('hierarchy_workspace'), {'phone':'9000000034', 'password':'Long-Secure-pass-789!', 'level':'salesman'})
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(phone='9000000034')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.salesman_profile.is_active)
        self.assertEqual(user.admin_profile.area, self.area)

    def test_it_unique_and_super_only(self):
        data = {'level':'it', 'country':self.country.pk, 'state':self.state.pk}
        self.assertTrue(AssignmentForm(data, actor=self.root).is_valid())
        self.assertFalse(AssignmentForm(data, actor=self.chain[0].user).is_valid())
        user = User.objects.create_user('itadmin', admin_role='scoped_admin')
        AdminProfile.objects.create(user=user, role='scoped_admin', hierarchy_level='it',
            appointed_by=self.root, country=self.country, state=self.state)
        self.assertFalse(AssignmentForm(data, actor=self.root).is_valid())
        self.client.force_login(user)
        self.assertEqual(self.client.post(reverse('hierarchy_workspace'), {}).status_code, 403)
        self.assertEqual(self.client.get(reverse('hierarchy_support', args=[999])).status_code, 404)

    def test_cannot_manage_ancestor(self):
        self.client.force_login(self.chain[2].user)
        self.assertEqual(self.client.post(reverse('hierarchy_toggle', args=[self.chain[0].pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse('hierarchy_password', args=[self.chain[0].pk])).status_code, 404)

    def test_super_toggle_and_password(self):
        self.client.force_login(self.root)
        self.assertEqual(self.client.post(reverse('hierarchy_toggle', args=[self.chain[1].pk])).status_code, 302)
        with self.assertRaises(PermissionDenied): authority(self.chain[-1].user)
        self.assertEqual(self.client.get(reverse('hierarchy_password', args=[self.chain[1].pk])).status_code, 200)

    def test_it_support_assignment_and_state_isolation(self):
        from .models import Complaint
        it = User.objects.create_user('support-user', admin_role='scoped_admin')
        ip = AdminProfile.objects.create(user=it, role='scoped_admin', hierarchy_level='it',
            appointed_by=self.root, country=self.country, state=self.state)
        local = Complaint.objects.create(submitted_by=self.root, subject='Local', description='Help', district=self.district)
        remote_district = District.objects.create(name='Remote', state=self.other)
        remote = Complaint.objects.create(submitted_by=self.root, subject='Remote', description='Help', district=remote_district, assigned_to=it)
        self.client.force_login(self.root)
        self.assertEqual(self.client.post(reverse('hierarchy_assign_support'), {'ticket': local.pk, 'admin': ip.pk}).status_code, 302)
        self.assertEqual(self.client.post(reverse('hierarchy_assign_support'), {'ticket': remote.pk, 'admin': ip.pk}).status_code, 200)
        self.client.force_login(it)
        self.assertContains(self.client.get(reverse('hierarchy_workspace')), 'Local')
        self.assertEqual(self.client.get(reverse('hierarchy_support', args=[remote.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse('hierarchy_support', args=[local.pk]), {'status':'resolved','resolution':'Fixed'}).status_code, 302)
        local.refresh_from_db()
        self.assertIsNotNone(local.resolved_at)

    def test_country_mapping_preserves_existing_accounts(self):
        unmapped = State.objects.create(name='New state', code='NS')
        self.client.force_login(self.root)
        self.assertEqual(self.client.post(reverse('hierarchy_geography'), {'country':self.country.pk, 'states':[unmapped.pk]}).status_code, 302)
        unmapped.refresh_from_db()
        self.assertEqual(unmapped.country, self.country)

    def test_phone_creation_and_login_flow(self):
        parent = self.root
        for index, level in enumerate(['country', 'state', 'district', 'area', 'salesman']):
            self.client.force_login(parent)
            phone = '900000004' + str(index)
            data = {'phone':phone, 'password':'Long-Secure-pass-789!', 'level':level,
                'country':self.country.pk, 'state':self.state.pk, 'district':self.district.pk, 'area':self.area.pk}
            self.assertEqual(self.client.post(reverse('hierarchy_workspace'), data).status_code, 302)
            parent = User.objects.get(phone=phone)
            self.assertEqual(parent.username, phone)
            self.assertTrue(parent.check_password(data['password']))
            self.client.logout()
            self.assertEqual(self.client.post(reverse('assigned_login'), {'username':phone, 'password':data['password']}).status_code, 302)
            response = self.client.get(reverse('assigned_dashboard'), follow=True)
            self.assertContains(response, parent.admin_profile.get_hierarchy_level_display() + ' dashboard')

    def test_super_cannot_skip_levels_and_duplicate_phone(self):
        from .admin_hierarchy import PhoneAccountForm
        self.assertFalse(AssignmentForm({'level':'state', 'country':self.country.pk, 'state':self.state.pk}, actor=self.root).is_valid())
        User.objects.create_user('registered', phone='9000000011')
        self.assertFalse(PhoneAccountForm({'phone':'9000000011','password':'Long-Secure-pass-789!'}).is_valid())
        self.assertFalse(PhoneAccountForm({'phone':'123','password':'123'}).is_valid())

    def test_cascading_filters_and_counts(self):
        self.client.force_login(self.root)
        response = self.client.get(reverse('hierarchy_workspace'), {'country': self.country.pk})
        self.assertEqual(response.context['team'].count(), 5)
        self.assertEqual(list(response.context['filter_form'].fields['state'].queryset), list(State.objects.filter(country=self.country).order_by('name')))
        response = self.client.get(reverse('hierarchy_workspace'), {'country':self.country.pk, 'state': self.state.pk, 'district': self.district.pk})
        self.assertEqual(response.context['team'].count(), 3)
        self.assertEqual(sum(item['total'] for item in response.context['counts']), 3)
        response = self.client.get(reverse('hierarchy_workspace'), {'country':self.country.pk, 'state':self.other.pk, 'district':self.district.pk})
        self.assertEqual(response.context['team'].count(), 0)
        self.client.force_login(self.chain[1].user)
        response = self.client.get(reverse('hierarchy_workspace'), {'state':self.other.pk})
        self.assertEqual(response.context['team'].count(), 3)

    def test_it_state_options_and_creation(self):
        self.client.force_login(self.root)
        response = self.client.get(reverse('hierarchy_states'), {'country':self.country.pk})
        self.assertEqual(len(response.json()['states']), 2)
        response = self.client.post(reverse('hierarchy_workspace') + '?create=it', {'level':'it', 'country':self.country.pk, 'state':self.state.pk, 'phone':'9000000066', 'password':'Long-Secure-pass-789!'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.get(phone='9000000066').admin_profile.hierarchy_level, 'it')
