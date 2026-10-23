# Functional follow-up: Offers, Community, and Health

Source: the user's registration, shopping/company profiles, offers, community, Gift Points, News, Health and Explore More testing report, supplied on 23 October 2026.

## Fixes

| Finding | Change |
|---|---|
| Visit Store opens WhatsApp or cannot find ownerless legacy stores | Store navigation and WhatsApp contacts now resolve separately. Legacy offers match registered businesses by a unique normalized business name. Messaging URLs are never used as Visit Store destinations. |
| HOTEL opens the unrelated TESTING business | Posting-account ownership is no longer assumed to identify a differently named merchant. Without a confirmed match, Visit Store opens that offer's merchant details instead of an unrelated company. Ambiguous names are not guessed. |
| WhatsApp fails or contacts are missing | Normalized national/international phone formats, avoided repeated country codes, and added fallback to the uniquely matched business's public contact. Invalid/missing contacts show an explicit unavailable state. Ownerless legacy offers prefer the matched store's public contact over their sample contact data. |
| Empty community posts are accepted | Server and browser validation require meaningful text or a valid photo. Whitespace/invisible-only posts and invalid attachments are rejected. Text-only and photo-only posts remain supported. |
| Member counts require manual refresh | Community pages and membership-status responses are not cached. Counts refresh on initial display, browser restoration, and window focus/visibility changes. Repeated joins are idempotent and pending memberships are excluded from approved counts. |
| Community JavaScript error | Guarded a missing share-button element discovered during browser testing. Prevented the loading overlay from running on a client-rejected empty submission. |
| Health titles, large unused player space, repeated breadcrumb names | Applied consistent display capitalization, constrained portrait-player width, balanced the information columns, and removed the category breadcrumb when it duplicates the item name. Published food/medical content was not rewritten. |

Offers are intentionally a listing of businesses with active offers, rather than a duplicate of every Shop listing. The Offers page now explains this and links to the complete business directory. No dummy offers were created to equalize the counts.

## Data still needed

- HOTEL's **2/2 OFFER**, MY IDDLI, NSG PUBLISHING COMPANY, and BIRTHDAY OFFER need verified WhatsApp contact details. Their current contacts are missing or invalid. They are not replaced with guessed numbers.
- Offers from merchants without a confirmed registered profile show the merchant details supplied with the offer. A full registered-company profile requires an actual matching business record.
- SUN VALLY's stored description was inspected read-only: it contains one meeting URL. No duplicate stored URL was found, and no meeting information was deleted.
- Missing business logos, descriptions and PIN/location data require the businesses' actual information. Successful registration was preserved; no new mandatory registration requirements were imposed.
- Gift Points testing remains blocked until a suitable test coupon/points allocation is supplied. A lack of matching published News stories is not itself a defect.

## Verification

- 41 automated tests passed, covering offer resolution/phone formatting, wrong-owner and ambiguous-name cases, active-offer access, community validation/counts, and existing regressions.
- Django checks and all 415 templates compiled successfully.
- Browser checks passed at 1440px, 768px and 390px: offer-to-store identity, WhatsApp target formatting, unavailable contacts, empty-post blocking, successful post persistence after refresh, immediate/focus-refreshed member counts, and Health layout/titles/breadcrumbs.
- No JavaScript page errors occurred in the final browser run.
- Browser tests used isolated fixtures. WhatsApp navigation was intercepted to check its destination without sending messages or claiming that a recipient's WhatsApp account was independently verified.

Local browser evidence is in the ignored `.audit-tools/functional-evidence/` directory.
