from datetime import time, timedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from . import models as m, tests as fixtures, services as svc


class FullGroupEditTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        fixtures.TuitionTests.setUpTestData.__func__(cls)

    def setUp(self):
        self.client.force_login(self.owner)
        self.url = reverse('tuition:batch_edit', args=[self.batch.uid])
        self.rule = m.ScheduleRule.objects.create(batch=self.batch, weekday=0, start_time=time(10),
            start_date=timezone.localdate(), end_date=timezone.localdate()+timedelta(days=14),
            duration_minutes=60, timezone_name='Asia/Kolkata', meeting_url='https://meet.google.com/abc')

    def data(self):
        return dict(name='Updated group', description='Music classes', new_subjects='Piano',
            capacity=3, mode='offline', location='Classroom', fee='', billing_period='monthly',
            weekdays=['1'], day_start_1='11:00', status='active')

    def test_prefill_and_update_existing_group(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'Save changes')
        self.assertEqual(response.context['form'].initial['day_start_0'], '10:00')
        enrolment = svc.decide(self.owner, self.application, 'accepted')
        svc.transfer(self.owner, enrolment, self.batch)
        counts = (m.Batch.objects.count(), m.Lesson.objects.count())
        response = self.client.post(self.url, self.data())
        self.assertEqual(response.status_code, 302, getattr(response, 'context', None))
        self.batch.refresh_from_db(); self.rule.refresh_from_db()
        self.assertEqual(self.batch.name, 'Updated group')
        self.assertFalse(self.rule.active)
        self.assertTrue(self.batch.rules.filter(active=True, weekday=1, start_time=time(11)).exists())
        self.assertEqual((m.Batch.objects.count(), m.Lesson.objects.count()), counts)
        self.assertTrue(self.batch.memberships.filter(enrolment=enrolment).exists())

    def test_other_teacher_denied_and_invalid_submission_unchanged(self):
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(self.url, self.data()).status_code, 403)
        self.client.force_login(self.owner)
        self.assertEqual(self.client.post(self.url, {**self.data(), 'day_start_1': ''}).status_code, 200)
        self.batch.refresh_from_db()
        self.assertEqual(self.batch.name, 'Morning')

    def test_past_class_preserved_and_future_conflict_rolls_back(self):
        past = timezone.now() - timedelta(days=2)
        session = m.ClassSession.objects.create(batch=self.batch, rule=self.rule,
            original_start=past, start=past, end=past+timedelta(hours=1), mode='offline', location='Old room')
        from unittest.mock import patch
        from django.core.exceptions import ValidationError
        with patch('tuition.services.generate', side_effect=ValidationError('Schedule conflict')):
            response = self.client.post(self.url, self.data())
        self.assertContains(response, 'Schedule conflict')
        self.rule.refresh_from_db(); self.batch.refresh_from_db()
        self.assertTrue(self.rule.active)
        self.assertEqual(self.batch.name, 'Morning')
        self.assertEqual(self.client.post(self.url, self.data()).status_code, 302)
        session.refresh_from_db()
        self.assertEqual(session.location, 'Old room')
        self.assertEqual(session.status, 'scheduled')
