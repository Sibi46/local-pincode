# OURPINCODE Report 2 — six fixes

Date: 25 October 2026
Source: `OURPINCODE-report 2.pdf`
Scope confirmed by owner: complete items 1–6 first. Items 7–11 (reviews, AI summaries, popularity, rewards and monthly reporting) belong to the separate review-feature work.

| Item | Finding and change |
| --- | --- |
| 1. Blank Refer & Earn link | Some business registration paths create accounts without referral codes. Employer and seeker dashboards now generate a missing code before displaying the link; the referral page uses the same helper. Existing codes remain unchanged and the account is locked while assigning a code. |
| 2. Job map | Initialize the map when the location step becomes visible, then recalculate its dimensions. Use the canonical tile endpoint and an explicit origin-compatible image referrer policy. If the map library or imagery fails, the form provides feedback and address/PIN entry remains available. Map click and dragged-marker coordinates still populate the submitted fields. |
| 3. Submitted job status | A submitted job is pending approval, not an applicant's job application. Publishing now opens the dashboard's pending-review section; drafts open the draft section. Added visible Under review, Choose plan and Drafts tabs with counts. The submission popup opens the submitted-job list. Approval requirements and application counts are preserved. |
| 4. Duplicate notification icons | Removed the second notification bell from the shared navigation while retaining the original bell, dropdown and notification content. |
| 5. Company identity when posting | The posting form identifies the current company above the steps, with its saved description when present. |
| 6. Company description | Added an optional, owner-editable description of up to 1,000 characters and an About section on the public profile. Existing profiles display an honest empty state until the owner provides content. Descriptions are escaped as text. Saving other profile fields preserves an existing description. |

## Verification

- 72 Django tests passed, covering these fixes plus registration, job applications, admin authorization and previous report regressions.
- Chromium checks passed at 1440, 768 and 390 pixels.
- Browser checks exercised the referral URL, visible company identity, deferred map dimensions, tile request referrer, map pin fields, tile failure feedback, pending-job redirect and visibility, description saving/display, and notification count.
- Map responses were mocked during automated browser tests; no automated tile scanning was performed.
- Django system checks and migration consistency checks passed.
- Browser writes used a separate local SQLite database and synthetic business account, not production records.

The map integration follows the [OpenStreetMap tile policy](https://operations.osmfoundation.org/policies/tiles/) for endpoint, attribution and browser referrer identification. Third-party map availability remains outside the application's control.

## Deployment

Includes an additive migration, `0059_companyprofile_description`. Back up the production database before applying it. The six fixes are isolated in the `fix/report-2` checkout so the other session's in-progress review features are not included.
