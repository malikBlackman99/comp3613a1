# COMP 3613 Assignment 2 — Submission Record

This package is kept separate from Assignment 1's instructions and report. It extends the existing StudentNest project and references the Assignment 1 design artifacts.

## Student and project

- **Name:** Add before PDF export.
- **ID:** Add before PDF export.
- **Project:** Student Accommodation — StudentNest, a student accommodation listing, management, and review application.
- **Assignment 1 project report:** [docs/report.md](../report.md).
- **Public application:** [https://faststarter-0g4k.onrender.com](https://faststarter-0g4k.onrender.com).
- **Repository:** [malikBlackman99/comp3613a1](https://github.com/malikBlackman99/comp3613a1).

## Existing design artifacts

- **Use case diagram:** [docs/diagrams/use-case.png](../diagrams/use-case.png).
- **Entity relationship diagram:** Mermaid ERD in [docs/report.md](../report.md), under Model diagram.
- **Application wireframe:** [docs/wireframes/accomodationplatform.png](../wireframes/accomodationplatform.png).
- **Named workflows:** View Listings (Student), Manage Listings (Landlord), Leave Review (Student).

## Test plans and implementation

- **Test plan and UAT cases:** [test-plans.md](test-plans.md).
- **Unit tests:** [`tests/test_accommodation_service.py`](../../tests/test_accommodation_service.py).
- **Integration/API tests:** [`tests/test_accommodation_api.py`](../../tests/test_accommodation_api.py).
- **Postman collection:** [StudentNest API Tests](../../postman/studentnest-api.postman_collection.json).
- **Run automated tests:** `python -m pytest -q`.
- **Run the application for manual UAT:** `python manage.py init` then `python manage.py run`.

The API exposes public listing read/search operations and authenticated listing, booking, and review operations. Review creation is restricted to users with a booking. The user directory endpoint is admin-only. Unit and integration test results must be captured from the actual commands before submission; UAT results and screenshots must come from the tester's browser run.

## Results and evidence

- **Unit test result:** 7 passed; terminal screenshot pending.
- **Integration test result:** 7 passed; terminal screenshot pending.
- **Postman collection result:** Pending collection run and screenshot.
- **Completed UAT report:** Pending execution; record outcomes in [test-plans.md](test-plans.md) and attach screenshots.

Do not represent pending checks as passing. Add the final screenshots, student details, and any UAT findings before exporting the single Assignment 2 PDF.
