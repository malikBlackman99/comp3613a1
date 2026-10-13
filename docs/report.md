# COMP 3613 Assignment 1

Draft this file with the Guide. **Update it after every phase milestone** before you pause. The use-case diagram is a UML PNG at `docs/diagrams/use-case.png`, linked from this file as `diagrams/use-case.png` (path relative to `docs/report.md`). The model diagram is Mermaid. **Embed wireframe images** as `wireframes/<file>` (files live in `docs/wireframes/`).

Do not put your student ID in this file if you will commit it. The PDF cover adds your name and ID at export time.

## Assigned project

Student Accommodation

## Three workflows

### 1.
View Listings (Student)

### 2.
Manage Listings (Landlord)

### 3.
Leave Review (Student)

## Use case diagram

![Use case diagram](diagrams/use-case.png)

View Listings is shared by Student and Landlord. View Listing Details is a separate use case that optionally extends View Listings; Leave Review remains separate. Manage Listings is associated with Landlord, and Leave Review with Student.

## Model diagram

First draft. Update this section in Phase 5 when polish revises the model, and note what changed.

Assumption: `Student` and `Landlord` are separate entities with their own profile data; each Listing is owned by one Landlord and can have many Reviews and Bookings, while a Student can write many Reviews and create many Bookings.

```mermaid
erDiagram
  STUDENT ||--o{ BOOKING : makes
  STUDENT ||--o{ REVIEW : writes
  LANDLORD ||--o{ LISTING : owns
  LISTING ||--o{ BOOKING : has
  LISTING ||--o{ REVIEW : receives

  STUDENT {
    int id PK
    string username
    string email
    string password_hash
    string full_name
    string university
    datetime created_at
  }

  LANDLORD {
    int id PK
    string username
    string email
    string password_hash
    string full_name
    string company_name
    datetime created_at
  }

  LISTING {
    int id PK
    int landlord_id FK
    string title
    string address
    string city
    decimal price_per_month
    string property_type
    string status
    text description
    bool available
    datetime created_at
  }

  BOOKING {
    int id PK
    int student_id FK
    int listing_id FK
    date start_date
    date end_date
    string status
    decimal total_price
    datetime created_at
  }

  REVIEW {
    int id PK
    int student_id FK
    int listing_id FK
    int rating
    text comment
    datetime created_at
  }
```

## Wireframes

### Student Accommodation overview

![Student Accommodation wireframe](wireframes/accomodationplatform.png)

<!-- student-build:wireframe-coverage
use_case: View Listings
image: docs/wireframes/accomodationplatform.png
covered: yes
-->

<!-- student-build:wireframe-coverage
use_case: Manage Listings
image: docs/wireframes/accomodationplatform.png
covered: yes
-->

<!-- student-build:wireframe-coverage
use_case: Leave Review
image: docs/wireframes/accomodationplatform.png
covered: yes
-->

### Phase 4 model notes

- LISTING.price_per_month — seen on the listing cards and detail screens; keep a numeric monthly price field with currency formatting.
- BOOKING.status — implied by the booking flow and listing detail; add a lifecycle state such as pending/confirmed/complete to match the workflow outcome.
- REVIEW.rating — seen on the review form; keep a 1-5 score that is validated on submit.
- LISTING.property_type / city / available — visible in the listing cards and list management screens; these fields should remain in the model for filtering and availability states.

The combined wireframe covers the three named workflows, but the post-submit path is still implicit: after a student books or leaves a review, the flow outcome is not shown. The design is usable, but the completion screen or confirmation state should be clarified before implementation.

## Theming

- **Colors:** Blue (`#1E4E8C`), gold (`#C9A227`), black (`#0A0A0A`)
- **Type:** Modern (DM Sans)
- **Tone:** Professional
- **Logo or wordmark:** Wordmark only (`StudentNest`); no logo

Applied as CSS tokens in `app/static/css/app.css` and carried through landing, login, register, and the authenticated shell. The starter dashboard demo at `/app` was removed; signed-in users go to listings. `/config` is kept.

## Implementation notes

### View Listings (Student)

Choice: listing grid and details are public; booking still requires sign-in.

<!-- student-build:code-check
workflow: View Listings (Student)
form: choice
layer: other
architecture_ok: yes
implement_confidence: 0.72
passed: yes
note: Student picked public listing grid; booking remains signed-in.
-->

<!-- student-build:code-check
workflow: View Listings (Student)
form: snippet
layer: model
architecture_ok: yes
implement_confidence: 0.65
passed: yes
note: Student added LISTING.created_at from the ERD; Guide kept PK on the table class.
-->

<!-- student-build:code-check
workflow: View Listings (Student)
form: snippet
layer: router
architecture_ok: yes
implement_confidence: 0.64
passed: yes
note: listings_view constructs AccommodationService(ListingRepository) and calls list_listings; no SQL in the route.
-->

<!-- student-build:code-check
workflow: View Listings (Student)
form: snippet
layer: repository
architecture_ok: yes
implement_confidence: 0.68
passed: yes
note: get_all used select(Listing) via db.exec in the repository; Guide added search filters to match the wireframe.
-->

Public `/listings` grid with search and View → detail. Booking on detail stays signed-in. Demo listings seed with landlord / landlordpass.

### Manage Listings (Landlord)

Choice A: image URL text field (`listingImg`) on Listing. Choice A: landlord average rating is the mean of all review ratings across that landlord's listings, computed in the service (`landlord_average_rating`). Profile shows listing count and average rating stars; Manage Listings page has the add form (name, address, city, price, type, details, image URL) and cards with View. Thin routes construct `ListingRepository` + `AccommodationService` and call methods — no SQL in routers.

<!-- student-build:code-check
workflow: Manage Listings (Landlord)
form: choice
layer: other
architecture_ok: yes
implement_confidence: 0.68
passed: yes
note: Student chose optional image URL text field on Listing for MVP images.
-->

<!-- student-build:code-check
workflow: Manage Listings (Landlord)
form: choice
layer: other
architecture_ok: yes
implement_confidence: 0.68
passed: yes
note: Student chose average of all reviews across the landlord's listings, computed in the service.
-->

<!-- student-build:code-check
workflow: Manage Listings (Landlord)
form: snippet
layer: model
architecture_ok: yes
implement_confidence: 0.60
passed: yes
note: Student added listingImg Optional[str] field; needed fixes for Optional casing and nullable.
-->

<!-- student-build:code-check
workflow: Manage Listings (Landlord)
form: snippet
layer: router
architecture_ok: yes
implement_confidence: 0.62
passed: yes
note: Student bound listingImg Form field and passed it into service.create_listing in create_listing route; no SQL in route.
-->

<!-- student-build:code-check
workflow: Manage Listings (Landlord)
form: snippet
layer: service
architecture_ok: yes
implement_confidence: 0.48
passed: partial
note: Student attempted listingImg parameter handling in create_listing service; three failed None-safety attempts, Guide completed that param line; student then completed landlord_average_rating correctly (fetch listings, collect ratings, avg or None).
-->

<!-- student-build:code-check
workflow: Manage Listings (Landlord)
form: snippet
layer: service
architecture_ok: yes
implement_confidence: 0.52
passed: yes
note: Student completed landlord_average_rating: get_user_listings, collect review ratings via review_repository, return avg or None. No raw SQL.
-->

Seed account landlord / landlordpass. Profile page shows listing count and average rating. `/manage-listings` is a searchable grid of the landlord's listings with View links and an **Add Listing** button; `/manage-listings/new` is the add form (name, address, city, pricing, details, image URL). Create redirects back to the manage grid.

### Leave Review (Student)

Choice A: the dropdown shows only listings the student has previously booked (wireframe's "Select Previously Booked Listing"). `Review.created_at` added from the ERD. Reviews page lists the student's reviews (listing thumbnail, title, stars, comment) then the form. Service `get_booked_listings` collects unique listing ids from the student's bookings via the booking repository. Thin route calls the service — no SQL in the router.

<!-- student-build:code-check
workflow: Leave Review (Student)
form: choice
layer: other
architecture_ok: yes
implement_confidence: 0.58
passed: yes
note: Student chose previously booked listings only for the review dropdown (matches wireframe).
-->

<!-- student-build:code-check
workflow: Leave Review (Student)
form: snippet
layer: model
architecture_ok: yes
implement_confidence: 0.55
passed: yes
note: Student added created_at datetime to ReviewBase; needed colon fix and stray import removed.
-->

<!-- student-build:code-check
workflow: Leave Review (Student)
form: snippet
layer: service
architecture_ok: yes
implement_confidence: 0.55
passed: yes
note: Student completed get_booked_listings: bookings via booking_repository, unique listing_ids set, resolve via get_listing. No raw SQL.
-->

<!-- student-build:code-check
workflow: Leave Review (Student)
form: snippet
layer: router
architecture_ok: yes
implement_confidence: 0.45
passed: yes
note: Student route snippet took two wrong attempts (fake query string, then passing a list into query=) before calling service.get_booked_listings(user.id) directly. Guide required the rewrite.
-->

Seed includes 12 landlords, 10 students, ~35 listings, bookings and reviews so the review dropdown and average ratings have data.

## Deployed app

Phase 6. Public Render URL (not localhost). Markers open this to mark the three workflows.

https://

## Logins

Every account a marker needs, including extra users you added. Starter accounts:

- bob / bobpass — regular user
- admin / adminpass — admin
- landlord / landlordpass — listing owner

## YouTube URL

## Session transcripts

Filled when the Guide builds the report: the agent writes each Guide chat to `docs/transcripts/<slug>.md` (Copilot Agent, Cursor, or OpenCode). `python manage.py report` packages them. Do not paste chats here during the build.

## Competency (student-judge)

Filled when the report is built. Guide runs student-judge, writes `docs/judge.md`, and export appends the scorecard here.

## Skill integrity

Filled by `python manage.py report`. Do not edit the course skills.
