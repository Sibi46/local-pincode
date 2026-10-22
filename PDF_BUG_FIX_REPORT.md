# OURPINCODE PDF findings and fixes

Source: the five-page `OURPINCODE.pdf` supplied on 22 October 2026.

The PDF contains 12 findings. Feature search and a light/dark switch are enhancements; the other findings describe defects or inconsistent behavior.

| # | Reported issue | Implemented change |
|---|---|---|
| 1 | Missing website favicon | Generated favicon assets from the existing logo, included them in interactive page headers, and made `/favicon.ico` return the image to anonymous visitors. |
| 2 | Profile photo does not update in the profile editor and homepage | Display saved personal photos in the profile-editor and homepage headers, retain business-logo fallback, and support personal photo uploads for business accounts too. The crop output now has a JPEG filename matching its content. |
| 3 | Question mark before Quiz Home | Replaced the damaged character with an accessible arrow icon and corrected the quiz title/loading text. |
| 4 | Registered business opens another tab and Back does not work | Business cards open in the current tab. Back uses same-origin browser history, with a business-directory link when history is unavailable. |
| 5 | Homepage searches only jobs; features are difficult to find | Added feature search with names and keywords, live results, a clear empty state, keyboard support, and a server-rendered fallback. Jobs remain a searchable destination. |
| 6 | No hover feedback while exploring features | Added visible hover and keyboard-focus feedback to the menu, shortcuts, and Explore tiles. |
| 7 | No light/dark switch | Added a labeled theme button to shared page headers, saved the choice locally, and adjusted content surfaces and text contrast in both themes. |
| 8 | Advertising Get Started leads through confusing sign-in/registration controls | Anonymous visitors get an advertising introduction with registration and sign-in choices. Sign-in retains the advertising destination. Logged-in registration pages show My Account, the redundant registration Add button is removed, and the approved-advertiser dashboard link is corrected. |
| 9 | Global Add button overlaps community actions | Removed the duplicated global floating registration button; each module retains its own relevant action. |
| 10 | Navigation icons differ between modules | Replaced separate navigation bars on affected pages with one shared component: Home, Offers, Flicks, Messages, and My Account. |
| 11 | Messages navigation icons are misaligned | Shared navigation gives all icons equal positions and dimensions. Adjusted the Messages viewport height and mobile header so controls do not overflow. |
| 12 | Sponsored ads open a new homepage tab | Sponsored cards stay in the current tab. Ads without a usable destination open a sponsored detail page with available business-profile, website, and contact links. Valid external destinations are preserved and click tracking remains active. |

## Verification

- 40 automated tests passed, including the new PDF regressions and existing offers, quiz, discovery, and ad-URL safety checks.
- Django system checks passed; all 412 templates compiled.
- Headless Chromium checks passed at 1440px, 768px, and 390px widths.
- Browser checks covered favicon access, feature search and empty results, Quiz Home, hover/focus feedback, theme persistence, same-tab business navigation and Back, advertising registration entry, sponsored details, photo crop/upload/save and header display, and consistent navigation geometry.
- No JavaScript page errors were observed in those browser flows.
- Browser tests used an isolated database and synthetic accounts; no production account or customer data was changed by the tests.

Browser evidence is stored locally under `.audit-tools/browser-evidence/` (excluded from Git). These checks cover the reported paths; they do not constitute a full regression test of every portal feature or verification of the ownership/content of third-party advertiser websites.
