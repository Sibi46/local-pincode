# Sowmiya K usability analysis — fixes

Date: 25 October 2026
Scope: offer filtering, profile/Home navigation, My Ask notification clarity and control alignment. Review/AI features remain separate from this change. The report's analytics charts and personalised recommendation proposals are new enhancements, not implemented or claimed as existing metrics here.

## Changes

1. **Offer categories:** category changes update the results, count and detail-modal data without a full page reload. Empty results retain a working reset action. Category links continue to work without JavaScript. Loading and failed-request messages are visible; previous results remain available on failure. Aborted or older responses cannot overwrite a newer selection. Back/Forward restores category results. Matching handles case differences in saved category values. Expired and unapproved offers are excluded; expired merchant landing pages are unavailable.
2. **Profile and Home navigation:** shared desktop, mobile and profile menus expose clear Home/account links. Corrected obsolete advertiser-dashboard and ad-posting URLs. Mobile navigation uses a keyboard-accessible button with expanded state. Escape closes menus and restores focus; clicking outside closes the profile dropdown. The existing coupon bottom navigation continues to provide Home and My Account.
3. **My Ask shortcuts:** separate, labelled Home, Notifications and Messages actions use different icons. Notifications show only the current user's unread account count and link to that user's appropriate dashboard inbox. Messages opens the existing private-message list. No notification preferences or delivery rules were changed.
4. **Alignment and loading:** filter chips, offer actions, profile controls, mobile links and My Ask shortcuts have consistent spacing and usable touch sizes. Replaced the shared base layout's old loading script with the previously tested handler; handled filter clicks no longer leave a blocking page overlay.

## Verification

- 65 Django tests passed, covering this report, the previous six-fix report, offers and contact mappings, earlier UI fixes, and My Ask privacy/connection behavior.
- Chromium checks passed at widths 1440, 1024, 800, 768, 390 and 320 pixels on Offers, My Ask and Gift Coupon activation pages.
- Browser checks covered matching/empty/reset filters, offer details after filtering, history navigation, rapid category switching with delayed responses, failed requests, menu keyboard/outside-click behavior, Home/account links and viewport overflow.
- Django system checks, migration consistency and JavaScript syntax checks passed. No new database migration is required.
- Test offers, notifications and authenticated browsing used a separate local SQLite database. No production test posts, offers, accounts or messages were created.

## Deployment notes

Work is isolated in `D:\Mypincode\usability-fixes`, branch `fix/usability-report`, based on the deployed Report 2 fixes. Cache versions were updated for the shared navigation script and layout stylesheet. The other session's review-feature work is not included.
