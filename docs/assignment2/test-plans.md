# COMP 3613 Assignment 2 — Test Plans

This document covers the StudentNest accommodation workflows in [Assignment 1's report](../report.md). It is a separate Assignment 2 artifact; it does not replace the Assignment 1 report.

## Scope and test environment

- **System:** StudentNest, FastAPI + SQLModel accommodation marketplace.
- **Test database:** isolated in-memory SQLite for automated tests; tests do not alter the developer or Render database.
- **Automated runner:** `python -m pytest -q`.
- **API collection:** [StudentNest API Tests](../../postman/studentnest-api.postman_collection.json).
- **Demo accounts for manual UAT:** `landlord / landlordpass`, `bob / bobpass`, and `admin / adminpass`.
- **Manual environment:** start with `python manage.py init --no-drop`, then `python manage.py run`; use `http://127.0.0.1:5000`. `--no-drop` preserves existing local data.

## User Acceptance Test plan

The tester should compare each screen and its outcome to the wireframe in [the Assignment 1 report](../report.md). Use a browser session logged in as the named role. Mark each case Pass/Fail and record the actual result; do not mark a case complete from the plan alone.

| ID | Workflow / role | Preconditions | User task | Acceptance criteria | Result |
|---|---|---|---|---|---|
| UAT-01 | View Listings / Student | Seed data exists; signed out or signed in as `bob` | Open Listings, search for a known city or title, open a matching listing, and search for a term with no match | Matching cards show title, city, monthly price, and an image or the app's fallback; detail shows the selected listing and its reviews; no-match search shows an empty state without an error. | Partial / issue: browse, search, and empty-state work; detail displays a literal rating-template placeholder instead of the rating |
| UAT-02 | Manage Listings / Landlord | Seed data exists; signed in as `landlord`; another landlord's listing is known | Search Manage Listings for another landlord's listing | The other landlord's listing is not shown in the current landlord's management list; an empty state is shown when no owned listing matches. | Pass: search for “palm residences” returned the no-listings empty state |
| UAT-03 | Leave Review / Student | Seed data exists; `bob` has a booking for at least one listing | Open Reviews, select a previously booked listing, submit a rating from 1–5 and a comment, then view the listing | The review is saved once, appears in the student's reviews and listing details, and displays the selected rating and comment. | Pass: success message shown and submitted review appears in the list |
| UAT-04 | Leave Review / Student | Signed in as `bob`; Bob has at least one previous booking and there is a listing he has not booked | Open the review form and inspect the available listing choices | The form only offers previously booked listings, so an unbooked listing cannot be selected through the visible UI. Direct API tampering is covered separately by IT-05. | Pass: visible review form restricts selection to previously booked listings |
| UAT-05 | Manage Listings / Landlord | Signed out | Inspect the signed-out navigation and available actions | Landlord management actions are not offered to a signed-out user; direct unauthenticated API creation is covered separately by IT-03. | Pass: signed-out UI only offers public listings and sign-in/register |

### UAT execution record

For each case, record the date, tester, browser, actual outcome, and Pass/Fail. Attach a screenshot of the outcome in the final submission. The application behavior has not been declared UAT-passed by this plan.

| ID | Date / tester | Actual result and screenshot filename | Pass/Fail |
|---|---|---|---|
| UAT-01 | November 11, 2026 / student | Listing cards and matching search results captured. No-match search for “hawaii” showed “No listings match your search.” The detail view shows reviews but renders the rating as a literal template placeholder (`{★* review.rating}`), so detail acceptance is not fully met. Screenshots: `Screenshot 2026-11-10 235951.png`, `Screenshot 2026-11-11 000053.png`, `Screenshot 2026-11-11 000118.png`, `Screenshot 2026-11-11 004833.png`. | Partial / rendering error documented |
| UAT-02 | November 11, 2026 / student | While signed in as landlord, searched Manage Listings for “palm residences”; page displayed “No listings yet. Use Add Listing to publish your first property.” This confirms that the other landlord's listing is not in this landlord's management results. Screenshot: `Screenshot 2026-11-11 004927.png`. | Pass |
| UAT-03 | November 11, 2026 / student | Review form and success message with the new review in the list captured. Screenshots: `Screenshot 2026-11-11 000523.png`, `Screenshot 2026-11-11 000543.png`. | Pass |
| UAT-04 | November 11, 2026 / student | The review form screenshot shows the “Select Previously Booked Listing” control populated with a booked listing; unbooked listings are not offered in this UI flow. Direct API rejection is verified separately by the integration test. Screenshot: `Screenshot 2026-11-11 000523.png`. | Pass (UI flow) |
| UAT-05 | November 11, 2026 / student | Signed-out listing/detail screenshots show public Listings and Sign in/Register, without landlord management controls. Direct unauthenticated API rejection is verified separately by the integration test. Screenshots: `Screenshot 2026-11-10 235951.png`, `Screenshot 2026-11-11 000118.png`. | Pass (UI flow) |

## Unit test plan

Unit tests isolate `AccommodationService` from persistence by substituting mocked repositories.

| ID | Module / behavior | Test data / action | Expected result | Automated test |
|---|---|---|---|---|
| UT-01 | Listing creation normalization | Whitespace around title/location/description/image; blank property type | Trim text, default type to Apartment, assign owner, start available | `test_create_listing_normalizes_input_and_sets_owner` |
| UT-02 | Booking price calculation | Listing at $1,500/month; 31-day stay | Pending booking with the service's minimum one-month price | `test_create_booking_calculates_monthly_total` |
| UT-03 | Booking date rule | End date equals or precedes start date | Raise `ValueError`; do not query or create a booking | `test_create_booking_rejects_non_positive_date_range` |
| UT-04 | Review eligibility | Student has no booking for listing | Raise `PermissionError`; do not persist a review | `test_create_review_requires_a_previous_booking` |
| UT-05 | Review creation | Student has booked listing; comment includes surrounding spaces | Preserve listing/student/rating and trim comment | `test_create_review_trims_comment_for_a_booked_listing` |
| UT-06 | Landlord rating aggregation | Three reviews across two owned listings | Return arithmetic average across the landlord's listings | `test_landlord_average_rating_uses_reviews_across_owned_listings` |
| UT-07 | Empty rating aggregation | Owned listing has no reviews | Return `None` | `test_landlord_average_rating_is_none_without_reviews` |

## Integration test plan

Integration tests run the FastAPI application against a fresh in-memory SQLite database and exercise HTTP routing, validation, authentication, service/repository interaction, persistence, and response schemas.

| ID | Area | Request / condition | Expected result | Automated test |
|---|---|---|---|---|
| IT-01 | Public listing search/detail | Search by city and fetch a listed item | `200`, matching JSON resource and detail; image field is `image_url` | `test_public_listing_list_search_and_detail` |
| IT-02 | Missing resource | Fetch unknown listing ID | `404` | `test_listing_detail_returns_404_for_missing_listing` |
| IT-03 | Listing authorization/create | Anonymous create, then authenticated create | Anonymous `401`; authenticated `201`; owner is the signed-in user | `test_listing_creation_requires_auth_and_records_owner` |
| IT-04 | Ownership scope | Landlord requests their listing collection with another user's listing present | Only the current user's listing is returned | `test_landlord_listing_collection_is_scoped_to_current_user` |
| IT-05 | Booking/review flow | Anonymous review, unbooked review, then booked review | `401`, `403`, then successful booking and `201` review; user collections contain only the actor's records | `test_booking_and_review_api_enforce_auth_and_booking_rule` |
| IT-06 | Request validation | Booking has equal start and end dates | `422`; no booking is persisted | `test_booking_rejects_non_increasing_dates` |
| IT-07 | User API authorization | Anonymous, authenticated regular user, then admin requests user directory | `401`, `403`, then `200`; response omits passwords | `test_user_directory_api_is_admin_only` |

The test fixtures create and dispose an isolated schema per test. They do not run `manage.py init`, drop the developer database, or use Render credentials.

## Test reporting evidence checklist

- [x] Unit suite run: `8 passed`.
- [x] Integration suite run: `7 passed`.
- [x] Save screenshots of both terminal test results for the submission.
- [x] Initial Postman collection run captured: 13 tests, 10 passed, 3 failed.
- [x] Postman rerun captured: 13 tests, 13 passed, 0 failed.
- [x] Complete UAT execution record; UAT-01 has a documented rendering issue.
- [x] Record the Postman assertion failure, fix, and passing rerun in the Assignment 2 submission document.

Latest automated run: November 10, 2026 — 15 total pytest cases passed (8 unit, 7 integration). The run reports deprecation warnings from the existing Starlette/httpx test-client combination and the existing naive `datetime.utcnow` model defaults; no test failures.

Pytest result screenshots:

- Unit tests: [8 passed](Screenshot%202026-11-10%20235426.png) (12 warnings).
- Integration tests: [7 passed](Screenshot%202026-11-10%20235531.png) (8 warnings).

Initial Postman run: November 11, 2026 — 13 tests, 10 passed, 3 failed. The failures were the landlord, student, and admin login checks: Postman followed each successful login redirect and exposed the final HTTP 200 response, while the collection only accepted 302/303. The subsequent authenticated requests passed, confirming the session cookies were used. The collection assertions were updated to accept a final 200 as well as an unfollowed 302/303.

Postman rerun: November 11, 2026 — 13 tests, 13 passed, 0 failed, 0 skipped, 0 errors.

- [Rerun summary](Screenshot%202026-11-11%20003854.png)
- [Rerun request results](Screenshot%202026-11-11%20003948.png)
- [Rerun full collection overview](Screenshot%202026-11-11%20004019.png)
- [Initial run summary](Screenshot%202026-11-11%20003017.png)
