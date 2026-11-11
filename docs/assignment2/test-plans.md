# COMP 3613 Assignment 2 — Test Plans

This document covers the StudentNest accommodation workflows in [Assignment 1's report](../report.md). It is a separate Assignment 2 artifact; it does not replace the Assignment 1 report.

## Scope and test environment

- **System:** StudentNest, FastAPI + SQLModel accommodation marketplace.
- **Test database:** isolated in-memory SQLite for automated tests; tests do not alter the developer or Render database.
- **Automated runner:** `python -m pytest -q`.
- **API collection:** [StudentNest API Tests](../../postman/studentnest-api.postman_collection.json).
- **Demo accounts for manual UAT:** `landlord / landlordpass`, `bob / bobpass`, and `admin / adminpass`.
- **Manual environment:** start with `python manage.py init`, then `python manage.py run`; use `http://127.0.0.1:5000`.

## User Acceptance Test plan

The tester should compare each screen and its outcome to the wireframe in [the Assignment 1 report](../report.md). Use a browser session logged in as the named role. Mark each case Pass/Fail and record the actual result; do not mark a case complete from the plan alone.

| ID | Workflow / role | Preconditions | User task | Acceptance criteria | Result |
|---|---|---|---|---|---|
| UAT-01 | View Listings / Student | Seed data exists; signed out or signed in as `bob` | Open Listings, search for a known city or title, and open a matching listing | Matching cards show title, city, monthly price, and available image; the detail page shows the selected listing and its reviews. Search with no match shows an empty state without an error. | Pending student execution |
| UAT-02 | Manage Listings / Landlord | Seed data exists; signed in as `landlord` | Open Manage Listings, search existing listings, add a listing using the wireframe fields, then return to the list | The landlord sees their own listings and the newly published listing; the new listing shows the submitted title, location, price, type, and description. Other landlords' listings are not in the landlord's management list. | Pending student execution |
| UAT-03 | Leave Review / Student | Seed data exists; `bob` has a booking for at least one listing | Open Reviews, select a previously booked listing, submit a rating from 1–5 and a comment, then view the listing | The review is saved once, appears in the student's reviews and listing details, and displays the selected rating and comment. | Pending student execution |
| UAT-04 | Leave Review / Student | Signed in as `bob`; choose a listing with no booking by `bob` | Attempt to submit a review for that listing (including by altering the request rather than the dropdown) | The application rejects the submission and does not create a review. | Pending student execution |
| UAT-05 | Manage Listings / Landlord | Signed out | Open a protected management page and attempt to create a listing | The app requires authentication; no listing is created. | Pending student execution |

### UAT execution record

For each case, record the date, tester, browser, actual outcome, and Pass/Fail. Attach a screenshot of the outcome in the final submission. The application behavior has not been declared UAT-passed by this plan.

| ID | Date / tester | Actual result and screenshot filename | Pass/Fail |
|---|---|---|---|
| UAT-01 | Pending | Pending | Pending |
| UAT-02 | Pending | Pending | Pending |
| UAT-03 | Pending | Pending | Pending |
| UAT-04 | Pending | Pending | Pending |
| UAT-05 | Pending | Pending | Pending |

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
| IT-06 | Request validation | Booking has equal start and end dates | `422`; no booking is created | `test_booking_rejects_non_increasing_dates` |
| IT-07 | User API authorization | Anonymous, regular user, then admin requests user directory | `401`, `401`, then `200`; response omits passwords | `test_user_directory_api_is_admin_only` |

The test fixtures create and dispose an isolated schema per test. They do not run `manage.py init`, drop the developer database, or use Render credentials.

## Test reporting evidence checklist

- [x] Unit suite run: `7 passed`.
- [x] Integration suite run: `7 passed`.
- [ ] Save screenshots of both terminal test results for the submission.
- [ ] Import and run the Postman collection; save its passing run summary.
- [ ] Complete the UAT execution record and attach screenshots for the executed cases.
- [ ] Record any failures, fixes, and retest results in the Assignment 2 submission document.

Latest automated run: November 10, 2026 — 14 total pytest cases passed (7 unit, 7 integration). The run reports deprecation warnings from the existing Starlette/httpx test-client combination and the existing naive `datetime.utcnow` model defaults; no test failures.
