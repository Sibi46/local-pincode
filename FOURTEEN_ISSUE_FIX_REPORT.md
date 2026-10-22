# Retest and fixes for the 14-issue report

Source: the user's pasted “Web Application Testing Report — All 14 Issues”.

## Findings and disposition

| ID | Reported problem | Change and verification |
|---|---|---|
| 01 | Flicks icon outside its intended placement | Retained a standard film icon in shared navigation. Checked equal icon positions at desktop, tablet and mobile widths, including Offers and Health. |
| 02 | Social icons open generic/wrong destinations | Replaced hardcoded platform-homepage links with configuration for official brand profiles. Empty, invalid, and platform-root URLs are excluded. Configuration/rendering tests pass. **Official OURPINCODE profile URLs are still needed to enable the real destinations; they have not been guessed.** |
| 03 | Add icon blocks Sign In | No global floating registration Add button is rendered on the affected routes. The existing explicit registration entry remains available. |
| 04 | Offers lacks Home navigation | Offers now uses shared navigation on all tested widths, alongside its visible Home breadcrumb. |
| 05 | Offer filtering and store navigation fail | Retested matching/empty categories and reset behavior. Standard offer cards expose Details and Visit Store when a business profile or destination exists. The offer dialog also retains its store link. |
| 06 | Desktop cards differ in size | Standardized offer image areas, copy spacing, and card sizing. Retained the earlier uniform discovery-card rules. |
| 07 | Quiz unavailable | Retested the participant page at `/quiz/play/`; the existing employer management route is preserved. |
| 08 | Modules overlap or become inaccessible | Removed separate Offers and Health navigation variants, retained bottom clearance, made Health tabs wrap, and placed the Health theme control in its header instead of over its tabs. Tested the reported module transitions and viewport widths. |
| 09 | Sponsor card follows each poster's dimensions | Sponsor carousel has a fixed 16:9 frame and full-size image area using `contain`. Tested tall and wide poster fixtures; frame dimensions remain unchanged across slides. |
| 10 | Offers disappears / Health appears only in Gift Points | Home, Offers, Flicks, Health, Messages, and My Account are consistently present in the same order with the same icons on tested routes. The current module receives an active state. |
| 11 | Register Your Business Back arrow fails | Form Back returns to the preceding business-introduction step; the next Back returns to account selection. The page-level control can then use same-origin history with Home as a fallback. Back buttons do not submit forms. |
| 12 | Mobile Nutrition missing; condition modules empty | Added a Nutrition tab and content panel on all widths. Health food cards now receive their saved condition mappings instead of an empty attribute, and filters use exact condition keys. Unmatched conditions and unpublished information have explicit empty states. No nutrition facts or medical guidance were invented or added. |
| 13 | Offers too small / poorly aligned on desktop | Added a centered 1200px page, a responsive grid with 300px minimum card sizing where space permits, readable text, and a single listing for flash and standard offers. Removed the separate Offers navigation and redundant spacing. |
| 14 | Duplicate Gift Points entry points | The homepage has one canonical Gift Points shortcut. Removed duplicates from its header, menu, footer, and Explore dialog. Feature search may still return the same destination intentionally. |

## Verification

- 40 automated tests pass across the new report regressions, previous fixes, quiz, discovery, and Health tests.
- Django checks and template compilation pass.
- Headless Chromium checks pass at 1440px, 768px, and 390px widths, with no JavaScript page errors in those flows.
- Browser coverage includes different sponsor aspect ratios; offer sizing, filtering and store links; navigation consistency and active states; Gift Points entry count; registration Back stages; mapped/unmatched Health conditions; and mobile Nutrition access.
- Browser evidence is under the ignored local `.audit-tools/fourteen-evidence/` directory. Fixtures and uploads are isolated from production data.

The report supplied no precise reproduction evidence for unspecified hidden modules. Verification covers the concrete reported paths and shared layout behavior, rather than claiming a complete audit of every portal screen.

## Remaining input

Provide the official Facebook, Instagram, LinkedIn, and YouTube profile URLs for BUG-02. The application reads them from `SOCIAL_FACEBOOK_URL`, `SOCIAL_INSTAGRAM_URL`, `SOCIAL_LINKEDIN_URL`, and `SOCIAL_YOUTUBE_URL`. Generic platform homepage links are no longer used as substitutes.
