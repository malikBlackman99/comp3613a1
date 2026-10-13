#!/usr/bin/env python3
"""FastStarter project CLI ? standard library argparse (no extra CLI library).

From the project root (venv active, deps installed; `.env` optional ? falls back to `.env.example`):

    python manage.py init
    python manage.py run
    python manage.py users
    python manage.py report --name "Student Name" --id "816000000"
    python manage.py usecase
    python manage.py skills-verify
"""

from __future__ import annotations

import argparse
from pathlib import Path


def _ensure_models_loaded() -> None:
    import app.models  # noqa: F401


def cmd_init(args: argparse.Namespace) -> None:
    """Create database tables (drops existing by default) and seed demo users."""
    from app.config import get_settings
    from app.database import drop_all, ensure_db_and_tables

    _ensure_models_loaded()
    if args.drop:
        print("Dropping all tables?")
        try:
            drop_all()
        except Exception as exc:  # noqa: BLE001
            from app.database import is_db_not_ready_error

            if not is_db_not_ready_error(exc):
                raise
            print(f"Database not ready yet while dropping ({exc}); continuing?")
    print("Creating tables?")
    ensure_db_and_tables()
    print(f"Database ready ({get_settings().database_uri}).")
    if getattr(args, "seed", True):
        cmd_seed(args)


def cmd_seed(args: argparse.Namespace) -> None:
    """Insert demo users, landlords, students, listings, bookings, and reviews."""
    from app.database import ensure_db_and_tables, get_cli_session
    from app.repositories.user import UserRepository
    from app.schemas.user import AdminCreate, RegularUserCreate
    from app.utilities.security import encrypt_password

    _ensure_models_loaded()
    ensure_db_and_tables()

    demo_users = [
        ("bob", "bob@example.com", "bobpass", "regular_user"),
        ("admin", "admin@example.com", "adminpass", "admin"),
        ("landlord", "landlord@example.com", "landlordpass", "regular_user"),
    ]

    landlord_names = [
        "alice", "carol", "dave", "erin", "frank",
        "grace", "heidi", "ivan", "judy", "mallory", "niamh",
    ]
    student_names = [
        "dylan", "peggy", "trent", "victor", "wendy",
        "xavier", "yara", "zoe", "oscar", "maya",
    ]

    for name in landlord_names:
        demo_users.append((name, f"{name}@landlord.com", f"{name}pass", "regular_user"))
    for name in student_names:
        demo_users.append((name, f"{name}@student.com", f"{name}pass", "regular_user"))

    created = 0
    skipped = 0
    with get_cli_session() as session:
        repo = UserRepository(session)
        for username, email, password, role in demo_users:
            if repo.get_by_username(username):
                print(f"  skip  {username} (already exists)")
                skipped += 1
                continue
            payload_cls = AdminCreate if role == "admin" else RegularUserCreate
            repo.create(
                payload_cls(
                    username=username,
                    email=email,
                    password=encrypt_password(password),
                    role=role,
                )
            )
            print(f"  create {username} ({role})")
            created += 1
        _seed_demo_listings(session, repo)
    print(f"Seed done - created {created}, skipped {skipped}.")
    print("Login with bob/bobpass, admin/adminpass, or landlord/landlordpass")


def _seed_demo_listings(session, user_repo) -> None:
    from datetime import date, timedelta

    from app.models.booking import Booking
    from app.models.listing import Listing
    from app.models.review import Review
    from app.repositories.booking import BookingRepository
    from app.repositories.listing import ListingRepository
    from app.repositories.review import ReviewRepository

    listing_repo = ListingRepository(session)
    if listing_repo.get_all():
        return

    landlord_usernames = [
        "landlord", "alice", "carol", "dave", "erin", "frank",
        "grace", "heidi", "ivan", "judy", "mallory", "niamh",
    ]
    landlords = [user_repo.get_by_username(n) for n in landlord_usernames]
    landlords = [u for u in landlords if u is not None]
    if not landlords:
        return

    student_usernames = [
        "bob", "dylan", "peggy", "trent", "victor",
        "wendy", "xavier", "yara", "zoe", "oscar", "maya",
    ]
    students = [user_repo.get_by_username(n) for n in student_usernames]
    students = [u for u in students if u is not None]

    property_types = ["Apartment", "Studio", "House", "Shared room"]
    cities = [
        "St. Augustine", "New Town", "Town Centre", "Chaguanas",
        "San Fernando", "Port of Spain", "Trinidad", "Couva",
    ]
    street_names = [
        "Campus Road", "New Town Street", "Centre Avenue", "Rose Drive",
        "Palm Street", "University Way", "Garden Lane", "Market Road",
        "Station Avenue", "Hillside Road", "River Path", "Beach Row",
    ]
    adjectives = [
        "Harbour View", "Oakline Court", "City Loop", "Palm Residences",
        "Sunrise Flats", "Green Gate", "Riverbend", "Hilltop Suites",
        "Campus Nest", "Metro Lofts", "Coral House", "Bamboo Lodge",
        "Starlight Apartments", "Cedar Hall", "Mango Court", "Reef Side",
        "Lantern House", "Silver Birch", "Golden Leaf", "Blue Horizon",
        "Quiet Corner", "Busy Bee", "Scholar House", "Transit Point",
        "Garden Spot", "Beachside", "Uptown Studio", "Midtown Flat",
        "West End House", "East Gate", "North View", "South Bank",
        "Central Court", "Park Lane", "College Road",
    ]

    listing_rows: list[Listing] = []
    for i, title in enumerate(adjectives):
        landlord = landlords[i % len(landlords)]
        price = 1200.0 + (i * 97) % 2800
        listing = Listing(
            title=title,
            address=f"{10 + i} {street_names[i % len(street_names)]}",
            city=cities[i % len(cities)],
            price_per_month=float(price),
            property_type=property_types[i % len(property_types)],
            status="available",
            description=f"Comfortable student accommodation near campus - {title}.",
            available=True,
            landlord_id=landlord.id,
        )
        listing_repo.create(listing)
        listing_rows.append(listing)

    booking_repo = BookingRepository(session)
    review_repo = ReviewRepository(session)
    today = date.today()
    for i, listing in enumerate(listing_rows):
        if i % 2 == 0 and students:
            student = students[i % len(students)]
            start = today - timedelta(days=60 - i)
            end = start + timedelta(days=90)
            booking = Booking(
                student_id=student.id,
                listing_id=listing.id,
                start_date=start,
                end_date=end,
                status="complete" if i % 4 == 0 else "confirmed",
                total_price=round(float(listing.price_per_month) * 3, 2),
            )
            booking_repo.create(booking)
            if i % 3 != 2:
                rating = [5, 4, 3, 5, 4, 2, 5, 4][i % 8]
                comments = [
                    "Great place, would book again.",
                    "Close to campus and quiet.",
                    "Manageable price, good transport.",
                    "Landlord was responsive.",
                    "Clean and well kept.",
                    "A bit small but fine for one.",
                    "Loved the neighborhood.",
                    "Would recommend to other students.",
                ]
                review = Review(
                    student_id=student.id,
                    listing_id=listing.id,
                    rating=rating,
                    comment=comments[i % len(comments)],
                )
                review_repo.create(review)


def cmd_run(args: argparse.Namespace) -> None:
    """Start the FastAPI app with Uvicorn."""
    import uvicorn

    from app.config import get_settings

    settings = get_settings()
    bind_host = args.host or settings.app_host
    bind_port = args.port or settings.app_port
    if args.reload is None:
        use_reload = settings.env.lower() != "production"
    else:
        use_reload = args.reload
    print(f"Starting FastStarter on http://{bind_host}:{bind_port} (reload={use_reload})")
    uvicorn.run(
        "app.main:app",
        host=bind_host,
        port=bind_port,
        reload=use_reload,
    )


def cmd_report(args: argparse.Namespace) -> None:
    """Build the submission package: merge judge, package transcripts, write PDF."""
    from app.report_pdf import export_report
    from app.skill_integrity import format_report, verify

    result = export_report(
        name=args.name,
        student_id=args.student_id,
        source=None if args.src is None else Path(args.src),
        output=None if args.output is None else Path(args.output),
    )
    print()
    print("Report package:")
    print(
        f"  Judge:       {'merged docs/judge.md' if result.judge_merged else 'MISSING - Guide must run student-judge first'}"
    )
    print(
        f"  Transcripts: {result.transcript_count} chat(s) in docs/transcripts/"
        + (
            ""
            if result.transcript_count
            else " (EMPTY - Guide must pull Copilot/Cursor/OpenCode chats first)"
        )
    )
    if result.transcript_zip:
        print(f"  Zip:         {result.transcript_zip.as_posix()}")
    print(f"  PDF:         {result.pdf_path.as_posix()}")
    print(format_report(verify()))


def cmd_transcripts(args: argparse.Namespace) -> None:
    """Package agent-written markdown under docs/transcripts/ (+ zip)."""
    from app.transcript_export import package_transcripts

    result = package_transcripts(make_zip=not args.no_zip)
    if result.found == 0:
        print(
            "Warning: no chat markdown in docs/transcripts/. "
            "The Guide agent must pull every Guide chat for this project "
            "(Copilot Agent, Cursor, or OpenCode) into docs/transcripts/<slug>.md first."
        )
        raise SystemExit(2)
    print(f"Submission package ready: {result.out_dir}")
    if result.zip_path:
        print(f"Zip for submission: {result.zip_path}")


def cmd_skills_verify(args: argparse.Namespace) -> None:
    """Check course skill files against .agents/skills.lock.json."""
    from app.skill_integrity import format_report, verify

    result = verify()
    print(format_report(result))
    if not result.ok:
        raise SystemExit(1)


def cmd_usecase(args: argparse.Namespace) -> None:
    """Render docs/diagrams/use-case.json to a UML use-case PNG."""
    from app.usecase_diagram import render_usecase_png

    dest = render_usecase_png(
        spec_path=None if args.spec is None else Path(args.spec),
        output=None if args.output is None else Path(args.output),
    )
    print(f"Wrote {dest}")


def cmd_skills_lock(args: argparse.Namespace) -> None:
    """Rewrite the skill lockfile (course authors only)."""
    from app.skill_integrity import write_lock

    dest = write_lock()
    print(f"Wrote {dest}")


def cmd_users(args: argparse.Namespace) -> None:
    """List users currently in the database."""
    from sqlmodel import select

    from app.database import get_cli_session
    from app.models.user import User

    _ensure_models_loaded()
    with get_cli_session() as session:
        users = session.exec(select(User)).all()
        if not users:
            print("No users found. Run: python manage.py init")
            return
        for user in users:
            print(
                f"  id={user.id}  username={user.username}  "
                f"role={user.role}  email={user.email}"
            )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python manage.py",
        description="FastStarter Python CLI ? init database, seed demo data, run the app.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser(
        "init",
        help="Create DB tables and seed demo users (drops existing tables by default)",
    )
    p_init.add_argument(
        "--no-drop",
        dest="drop",
        action="store_false",
        help="Create tables without dropping existing ones",
    )
    p_init.set_defaults(drop=True)
    p_init.add_argument(
        "--no-seed",
        dest="seed",
        action="store_false",
        help="Skip seeding demo users after creating tables",
    )
    p_init.set_defaults(seed=True)
    p_init.set_defaults(func=cmd_init)

    p_run = sub.add_parser("run", help="Start the web app")
    p_run.add_argument("--host", default=None)
    p_run.add_argument("--port", type=int, default=None)
    p_run.add_argument("--reload", action="store_true")
    p_run.set_defaults(func=cmd_run)

    p_seed = sub.add_parser("seed", help="Insert demo users")
    p_seed.set_defaults(func=cmd_seed)

    p_report = sub.add_parser("report", help="Build the report package")
    p_report.add_argument("--name", required=True)
    p_report.add_argument("--id", dest="student_id", required=True)
    p_report.add_argument("--src", default=None)
    p_report.add_argument("--output", default=None)
    p_report.set_defaults(func=cmd_report)

    p_usecase = sub.add_parser("usecase", help="Render the UML use-case diagram")
    p_usecase.add_argument("--spec", default=None)
    p_usecase.add_argument("--output", default=None)
    p_usecase.set_defaults(func=cmd_usecase)

    p_verify = sub.add_parser("skills-verify", help="Verify course skill integrity")
    p_verify.set_defaults(func=cmd_skills_verify)

    p_lock = sub.add_parser("skills-lock", help="Rewrite the course skill lock file")
    p_lock.set_defaults(func=cmd_skills_lock)

    p_users = sub.add_parser("users", help="List current users")
    p_users.set_defaults(func=cmd_users)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
