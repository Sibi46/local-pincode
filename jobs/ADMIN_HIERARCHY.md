# Admin hierarchy

Super Admin manages all new team accounts. Country/state/district/PIN-code filters and country-name or phone search show scoped accounts and counts by role. Child locations appear after selecting their parent. Each role has a dashboard titled for that role. Each country admin creates state admins;
state admins create district admins; district admins create area admins; area admins
create salesmen. An area is one existing PIN code. Super Admin alone creates one
State IT Admin per state, assigns existing complaints to that admin, and monitors activity.
IT access is limited to assigned complaints in that state; it grants no content moderation.

Entry: /admin-team/ from the Super Admin sidebar. Login: /admin-workspace/login/.
First use Countries and state mapping to create a country and associate existing states.
No country is inferred or automatically assigned to existing data.
Creation requires a 10-digit phone number and password; the phone is also the internal username. Existing username logins remain valid. Super Admin creates only Country Admin and State IT Admin, while every other admin creates the next level. Staff privileges are never granted.
Super Admin and ancestor admins can suspend/reactivate descendants and reset passwords.
Suspending any ancestor blocks the descendant workspace immediately. Existing legacy
section admins remain separate and cannot be edited through the new hierarchy.

Migration jobs/0055 is additive: Country plus nullable geographic links and blank-by-default
hierarchy level. Back up the database before release, apply migrations before restarting
new code. No account conversion or data deletion. Do not reverse migrations as rollback;
retain additive schema when rolling back application code.

Salesman accounts reuse coupons.Salesman, but this hierarchy release provides their
assigned-area workspace only. Existing coupon sales routes are deliberately not granted
because they do not enforce the new PIN-code boundary. Legacy sales accounts are unchanged.

IT uniqueness is serialized using a State row lock in the account creation workflow;
manual database/Django-admin writes must not bypass this workflow. SQLite tests do not
prove MySQL concurrency. Production deployment and browser/device verification are separate.

Validation (local SQLite, 2026-10-13): 34 tests passed across
jobs.test_admin_hierarchy and jobs.test_assigned_admin, including hierarchy scopes,
creation, ancestor suspension, password access, IT isolation and legacy permissions.
Django system check passed; makemigrations --check --dry-run reported no changes.
No production migration, push or deployment performed.

Phone-login and hierarchy-filter update: 38 tests passed across the same two suites; Django checks, migration drift check and node --check static/js/admin-hierarchy.js passed. No new schema change. Browser/device interaction has not been manually verified.
