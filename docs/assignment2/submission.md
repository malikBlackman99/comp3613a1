# COMP 3613 Assignment 2 — Submission Record

This package is kept separate from Assignment 1's instructions and report. It extends the existing StudentNest project and references the Assignment 1 design artifacts.

## Student and project

- **Name:** Malik Blackman.
- **Student ID:** Printed on the PDF cover only; intentionally omitted from this Markdown file.
- **PDF submission:** [Assignment 2 submission PDF](Assignment2-Submission.pdf).
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
- **Run the application for manual UAT:** `python manage.py init --no-drop` then `python manage.py run` (preserves existing local data).

The API exposes public listing read/search operations and authenticated listing, booking, and review operations. Review creation is restricted to users with a booking. The user directory endpoint is admin-only. Automated test results are recorded from the actual pytest run; UAT results, Postman run results, and their screenshots must come from the tester's own runs.

## Results and evidence

- **Unit test result:** 8 passed; [terminal screenshot](Screenshot%202026-11-10%20235426.png).
- **Integration test result:** 7 passed; [terminal screenshot](Screenshot%202026-11-10%20235531.png).
- **Combined pytest run:** 15 passed; 19 deprecation warnings. Individual unit/integration output screenshots are included.
- **Postman collection result:** Rerun passed all 13 checks (0 failed, 0 skipped, 0 errors). [Rerun summary screenshot](Screenshot%202026-11-11%20003854.png). The initial 10 passed / 3 failed run exposed redirect-following assertions, which were corrected in the collection.
- **UAT evidence:** UAT-02 through UAT-05 passed. UAT-01 is partial: the “hawaii” search displays the expected no-results message, but the detail screenshot shows a literal rating-template placeholder instead of a rendered rating. The landlord's search for another landlord's “palm residences” listing returned the empty state, confirming owner-scoped management results. See the evidence table and screenshots in [test-plans.md](test-plans.md).

The UAT execution record and screenshots are included in this Assignment 2 submission package. UAT-01's listing-detail rating rendering issue remains documented as an unresolved defect.
