from datetime import date
from unittest.mock import patch
from django.test import SimpleTestCase
from .forms import LearnerForm


class GuardianAgeTests(SimpleTestCase):
    def data(self):
        return dict(name='Student', age=17, pincode='600001', interests='',
            relationship='Parent', attestation='I am authorized')

    def test_minor_requires_guardian_contact(self):
        form = LearnerForm(self.data())
        self.assertFalse(form.is_valid())
        self.assertIn('guardian_name', form.errors)
        self.assertIn('phone', form.errors)
        form = LearnerForm({**self.data(), 'guardian_name': 'Parent', 'phone': '9876543210'})
        self.assertTrue(form.is_valid(), form.errors)

    @patch('tuition.forms.timezone.localdate', return_value=date(2026, 10, 12))
    def test_dob_overrides_age_and_eighteenth_birthday(self, today):
        adult = LearnerForm({**self.data(), 'dob': '2008-10-12', 'self_registration': True})
        self.assertTrue(adult.is_valid(), adult.errors)
        minor = LearnerForm({**self.data(), 'dob': '2008-10-13', 'age': 18})
        self.assertFalse(minor.is_valid())
        self.assertIn('guardian_name', minor.errors)
