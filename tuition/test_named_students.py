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
        self.client.post(url, {**self.data(), 'subject': other.pk})
        self.assertFalse(m.Enrolment.objects.exists())
