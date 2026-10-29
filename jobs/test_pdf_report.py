import io
import tempfile
from pathlib import Path
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from .features import search_features
from .models import User, CompanyProfile, AdPost, Advertiser


@override_settings(ALLOWED_HOSTS=['testserver'], SECURE_SSL_REDIRECT=False,
    PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'],
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}})
class PdfReportTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = User.objects.create_user('report-person', user_type='individual', pincode='600001')
        cls.owner = User.objects.create_user('report-owner', user_type='shop', pincode='600001')
        cls.company = CompanyProfile.objects.create(user=cls.owner, company_name='Sample store')
        cls.post = AdPost.objects.create(user=cls.owner, company_name='Sample store', description='Local sale', image='ad_posts/sample.png', status='approved')

    def test_favicon_is_public_image(self):
        response = self.client.get('/favicon.ico')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/x-icon')
        self.assertTrue(b''.join(response.streaming_content))

    def test_feature_search_has_server_fallback_and_no_matches(self):
        response = self.client.get('/?feature=QUIZ')
        self.assertContains(response, 'Find a feature')
        self.assertEqual(response.context['feature_matches'][0]['url'], '/quiz/play/')
        self.assertContains(self.client.get('/?feature=xyzmissing'), 'No features found.')
        self.assertEqual(search_features('career')[0]['name'], 'Jobs')

    def test_photo_upload_displays_on_home_and_edit_for_all_account_types(self):
        with tempfile.TemporaryDirectory() as media, override_settings(MEDIA_ROOT=media):
            for user in (self.person, self.owner):
                self.client.force_login(user)
                data = io.BytesIO(); Image.new('RGB', (20, 20), 'blue').save(data, format='PNG')
                response = self.client.post('/profile/edit/', {'first_name': 'Photo', 'photo': SimpleUploadedFile('photo.png', data.getvalue(), content_type='image/png')})
                self.assertEqual(response.status_code, 302)
                user.refresh_from_db()
                self.assertTrue(Path(user.seeker.photo.path).exists())
                for route in ('/', '/profile/edit/'):
                    self.assertContains(self.client.get(route, follow=True), user.seeker.photo.url)

    def test_quiz_home_link_has_no_question_mark(self):
        response = self.client.get('/quiz/play/')
        self.assertNotContains(response, '? Home')
        self.assertContains(response, 'fa-arrow-left')

    def test_business_strip_stays_in_same_tab_and_back_has_fallback(self):
        response = self.client.get('/register/?type=company')
        self.assertContains(response, '/business/' + self.company.company_id + '/')
        self.assertNotContains(response, 'data-name="sample store" target="_blank"')
        response = self.client.get(reverse('business_profile', args=[self.company.company_id]))
        self.assertContains(response, 'href="/businesses/" aria-label="Back to businesses"')

    def test_advertise_entry_explains_registration_instead_of_login_bounce(self):
        response = self.client.get('/advertise/register/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Register Your Business')
        self.assertContains(response, '/login/?next=/advertise/register/')
        self.client.force_login(self.person)
        self.assertContains(self.client.get('/register/?type=company'), 'My Account')

    def test_shared_navigation_and_no_global_plus(self):
        self.client.force_login(self.person)
        for path in ('/', '/messages/', '/profile/edit/', '/quiz/play/', '/community/local-heroes/'):
            response = self.client.get(path)
            self.assertContains(response, 'class="opc-bottom-nav"', count=1)
            self.assertNotContains(response, 'class="bn-plus-btn"')
            self.assertContains(response, 'fa-film')

    def test_sponsored_ad_without_website_goes_to_details_with_store_link(self):
        response = self.client.get(reverse('adpost_click_track', args=[self.post.pk]))
        self.assertRedirects(response, reverse('sponsored_post_detail', args=[self.post.pk]))
        self.post.refresh_from_db(); self.assertEqual(self.post.clicks, 1)
        detail = self.client.get(response.url)
        self.assertContains(detail, 'Local sale')
        self.assertContains(detail, '/business/' + self.company.company_id + '/')

    def test_sponsored_ad_homepage_destination_uses_details(self):
        self.post.website = 'https://testserver/'
        self.post.save()
        self.assertRedirects(self.client.get(reverse('adpost_click_track', args=[self.post.pk])), reverse('sponsored_post_detail', args=[self.post.pk]))

    def test_sponsored_ad_valid_website_is_preserved(self):
        self.post.website = 'https://store.example.com/sale'
        self.post.save()
        response = self.client.get(reverse('adpost_click_track', args=[self.post.pk]))
        self.assertEqual(response.url, self.post.website)

    def test_sponsored_banner_details_work_without_website(self):
        advertiser = Advertiser.objects.create(user=self.owner, business_name='Sample store', status='approved', banner_image='banners/sample.png')
        response = self.client.get(reverse('sponsored_banner_detail', args=[advertiser.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Visit business profile')
