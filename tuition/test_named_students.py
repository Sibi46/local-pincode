from django.test import TestCase
from django.urls import reverse
from . import tests as fixtures, models as m


class NamedStudentTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        fixtures.TuitionTests.setUpTestData.__func__(cls)
        cls.parent.phone = '9876543210'; cls.parent.save()
        cls.subject = m.Subject.objects.create(name='Music', slug='music')
        cls.lesson.subjects.add(cls.subject)

    def data(self, name='Child'):
        return {'name': name, 'phone': self.parent.phone, 'subject': self.subject.pk}

    def test_name_creates_private_group_record(self):
        self.client.force_login(self.owner)
        url = reverse('tuition:group_students', args=[self.batch.uid])
        self.assertNotContains(self.client.get(url), 'name="application"')
        self.assertEqual(self.client.post(url, self.data()).status_code, 302)
        enrolment = m.Enrolment.objects.get(lesson=self.lesson)
        self.assertNotEqual(enrolment.learner_id, self.child.pk)
        self.assertIsNone(enrolment.learner.user_id)
        self.assertFalse(enrolment.learner.guardians.exists())
        self.assertEqual(enrolment.membership.batch, self.batch)

    def test_permissions_capacity_and_empty_name(self):
        url = reverse('tuition:group_students', args=[self.batch.uid])
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(url, self.data('Student')).status_code, 403)
        self.client.force_login(self.owner)
        self.client.post(url, self.data('   '))
        self.assertFalse(m.Enrolment.objects.exists())
        self.batch.capacity = 1
        self.batch.save()
        self.client.post(url, self.data('First'))
        count = m.Learner.objects.count()
        self.assertContains(self.client.post(url, self.data('Second')), 'Group is full.')
        self.assertEqual(m.Learner.objects.count(), count)

    def test_unregistered_phone_and_unrelated_subject_rejected(self):
        self.client.force_login(self.owner)
        url = reverse('tuition:group_students', args=[self.batch.uid])
        response = self.client.post(url, {**self.data(), 'phone': '9999999999'})
        self.assertContains(response, 'not registered to an active account')
        other = m.Subject.objects.create(name='Other', slug='other')
        from django.core.exceptions import ValidationError
        from .services import add_named_student
        with self.assertRaises(ValidationError):
            add_named_student(self.owner, self.batch, 'Child', self.parent.phone, other)
        self.assertFalse(m.Enrolment.objects.exists())

    def test_parent_name_and_group_selection(self):
        self.client.force_login(self.owner)
        batch = m.Batch.objects.create(lesson=self.lesson, name='Evening', mode='online', capacity=3)
        response = self.client.post(reverse('tuition:group_students', args=[self.batch.uid]),
            {**self.data(), 'group':batch.pk, 'guardian_name':'Parent Name'})
        self.assertEqual(response.status_code, 302)
        enrolment = m.Enrolment.objects.get(lesson=self.lesson)
        self.assertEqual(enrolment.membership.batch, self.batch)
        self.assertEqual(enrolment.learner.guardian_name, 'Parent Name')
        self.assertFalse(enrolment.learner.guardians.exists())
        self.assertIsNone(enrolment.learner.user_id)

    def test_phone_check_scoped_records_and_permissions(self):
        from django.core.cache import cache
        cache.clear()
        self.client.force_login(self.owner)
        url = reverse('tuition:student_phone_check', args=[self.teacher.uid])
        response = self.client.post(url, {'phone':self.parent.phone})
        self.assertTrue(response.json()['registered'])
        self.assertEqual(response.json()['students'], [])
        self.client.post(reverse('tuition:group_students', args=[self.batch.uid]), {**self.data(), 'guardian_name':'Own parent name'})
        response = self.client.post(url, {'phone':self.parent.phone})
        self.assertEqual(response.json()['students'], [{'name':'Child','guardian_name':'Own parent name'}])
        self.assertIn('no-store', response['Cache-Control'])
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(url, {'phone':self.parent.phone}).status_code, 403)

    def test_popup_registration_keeps_teacher_logged_in_and_rejects_duplicates(self):
        from django.core.cache import cache
        from django.contrib.auth import get_user_model
        cache.clear()
        self.client.force_login(self.owner)
        url = reverse('tuition:student_account_register', args=[self.teacher.uid])
        data = {'phone':'9000000089','name':'New Parent','password1':'Secure-Parent-789!', 'password2':'Secure-Parent-789!'}
        self.assertEqual(self.client.post(url, data).status_code, 200)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.owner.pk)
        user = get_user_model().objects.get(phone=data['phone'])
        self.assertTrue(user.check_password(data['password1']))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.admin_role)
        self.assertFalse(m.GuardianLink.objects.filter(user=user).exists())
        self.assertEqual(self.client.post(url, data).status_code, 400)
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(url, data).status_code, 403)

    def test_teacher_entry_and_other_group_rejected(self):
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(reverse('tuition:teacher_students', args=[self.teacher.uid])).status_code, 200)
        self.assertContains(self.client.get(reverse('tuition:profile', args=[self.teacher.slug])), 'Add student')
        other_teacher = m.TeacherProfile.objects.create(owner=self.other, kind='teacher', name='Other', status='approved', pincode='600001')
        lesson = m.Lesson.objects.create(teacher=other_teacher, name='Other', capacity=5, start_date=self.lesson.start_date)
        batch = m.Batch.objects.create(lesson=lesson, name='Other', capacity=5)
        response = self.client.post(reverse('tuition:group_students', args=[self.batch.uid]), {**self.data(), 'group':batch.pk})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(m.Enrolment.objects.get().membership.batch, self.batch)
        self.assertFalse(m.Enrolment.objects.filter(lesson=lesson).exists())
        self.client.force_login(self.other)
        self.assertNotContains(self.client.get(reverse('tuition:profile', args=[self.teacher.slug])), 'Add student')

    def test_phone_actions_require_csrf_and_approved_teacher(self):
        from django.test import Client
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        url = reverse('tuition:student_account_register', args=[self.teacher.uid])
        self.assertEqual(client.post(url, {}).status_code, 403)
        self.client.force_login(self.owner)
        self.teacher.status = 'pending'; self.teacher.save()
        self.assertEqual(self.client.post(url, {}).status_code, 403)
        self.assertEqual(self.client.post(reverse('tuition:student_phone_check', args=[self.teacher.uid]), {'phone':self.parent.phone}).status_code, 403)

    def test_save_without_group_then_lookup_and_reuse(self):
        from django.core.cache import cache
        cache.clear()
        self.client.force_login(self.owner)
        url = reverse('tuition:teacher_students', args=[self.teacher.uid])
        response = self.client.get(url)
        self.assertNotContains(response, 'name="group"')
        self.assertNotContains(response, 'name="subject"')
        data = {'name':'Saved student', 'phone':self.parent.phone, 'guardian_name':'Saved parent'}
        self.assertEqual(self.client.post(url, data).status_code, 302)
        learner = m.Learner.objects.get(name='Saved student')
        self.assertFalse(learner.enrolments.exists())
        self.assertIsNone(learner.user_id)
        self.assertFalse(learner.guardians.exists())
        self.client.post(url, data)
        self.assertEqual(m.Learner.objects.filter(name='Saved student').count(), 1)
        lookup = reverse('tuition:student_phone_check', args=[self.teacher.uid])
        self.assertEqual(self.client.post(lookup, {'phone':self.parent.phone}).json()['students'],
            [{'name':'Saved student', 'guardian_name':'Saved parent'}])
        group_url = reverse('tuition:group_students', args=[self.batch.uid])
        self.assertEqual(self.client.post(group_url, data).status_code, 302)
        self.assertEqual(m.Enrolment.objects.get().learner_id, learner.pk)
        self.assertContains(self.client.post(group_url, data), 'already in this group')
        self.assertEqual(m.Enrolment.objects.count(), 1)

    def test_standalone_rejects_unregistered_phone_and_other_owner(self):
        self.client.force_login(self.owner)
        url = reverse('tuition:teacher_students', args=[self.teacher.uid])
        self.assertContains(self.client.post(url, {'name':'No account', 'phone':'9999999999'}),
            'not registered')
        self.assertFalse(m.Learner.objects.filter(name='No account').exists())
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(url, self.data()).status_code, 403)
