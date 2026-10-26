Report 2 implementation
=======================

Work applies to the current application in `D:\Mypincode\ourpincode` (the directory used by `start-local.ps1`).

1. Legacy business and jobseeker accounts receive a referral code before a share link is rendered. The business dashboard has a permanent Refer & Earn link.
2. The Leaflet job map initializes when the Location step is visible and recalculates its dimensions. Missing map scripts or tiles show a fallback; address entry remains available.
3. Publishing redirects to Under Review; saving a draft redirects to Drafts. The dashboard exposes counts and links for approval, drafts, plan selection, payment review, expired and closed jobs. Closing the success popup reveals the submitted job.
4. Removed the duplicate notification bell from shared navigation.
5. The post-job header displays the company name.
6. Owners can edit a description (up to 1,000 characters) in Company Profile. It appears on the public business page and directory cards.
7. Signed-in customers can submit or update one 1–5 star review per business. Self reviews and invalid submissions are rejected. Text is escaped. Existing Flick post likes are accessible on business profiles.
8. Public profiles show a statistical review snapshot. The monthly command can also generate a clearly labeled AI summary using the existing Anthropic integration. No credentials are added. Without AI configuration, statistics remain available.
9. The business directory supports highest rated, most reviewed, and trending (new review count over the last 30 days), combined with a pincode filter.
10. Reviewers receive Community Reviewer, Local Guide (3 businesses), or Community Expert (10 businesses) badges. Business owners may opt into 1–50% review vouchers; the default is off. Any star rating qualifies. A first review grants one voucher, updating the review does not issue another, vouchers expire after 30 days, and only the business owner can redeem one once. These discounts are redeemed at the business rather than through the gift-voucher payment system.
11. Monthly review reports appear privately to owners on their business page and create an in-app notification. Optional email delivery records successful sends to avoid duplicates on subsequent runs.

Deployment
----------

The migration has been applied to the local `db.sqlite3`. A pre-migration backup is saved as `db.report2-before-changes.sqlite3`. Apply the migration separately when deploying elsewhere:

```powershell
python manage.py migrate
```

Schedule this command on the first of each month in the deployment environment (it defaults to the previous calendar month):

```powershell
python manage.py send_business_review_reports --ai --email
```

`--ai` requires `ANTHROPIC_API_KEY` and sends up to 100 review texts/ratings per business to that provider, without reviewer names. The existing model is the default; `REVIEW_SUMMARY_MODEL` can override it in Django settings. Provider failures fall back to statistics. AI output is labeled and is rendered as escaped text.

`--email` requires the deployment's email backend and an owner email address. Omit it to use in-app delivery only. Omit `--ai` for statistics only. Use `--month YYYY-MM` for a specific month. Existing reports are preserved on reruns. No production scheduler, email or AI call is enabled automatically by this patch.

Validation
----------

```powershell
python manage.py check --settings=jobportal.test_settings
python manage.py makemigrations --check --dry-run --settings=jobportal.test_settings
python manage.py test jobs.test_report2 jobs.test_business_registration jobs.test_corrections jobs.test_application_flow --settings=jobportal.test_settings --noinput
```

All 60 combined regression tests passed, including the production news submission, usability, registration and application tests. Django system checks and the migration consistency check passed. Production's existing `0059_companyprofile_description` migration is preserved; review features are added by `0060_business_reviews_and_rewards`.

Homepage follow-up
------------------

The homepage introduction now explains the site's purpose with three green, purple and yellow cards inspired by the supplied reference: discover nearby shops/services/offers/jobs, register a business to reach local customers, and join neighbourhood communities. Each card has a working destination. The business registration link preselects Business. The cards replace the seasonal Diwali promotion, sit side by side on desktop, and support swipe, previous/next buttons, dots and keyboard navigation on mobile. No automatic rotation interrupts reading.

Browser checks passed at 320, 390, 768 and 1280 pixels: no page or text overflow, working arrows/dots/keyboard navigation, and no JavaScript errors. Screenshots are saved in the workspace `qa-report` directory.
