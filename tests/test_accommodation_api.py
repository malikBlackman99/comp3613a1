from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.listing import Listing
from app.models.user import User
from app.utilities.security import create_access_token


def authenticate(client: TestClient, user: User) -> None:
    client.cookies.set(
        "access_token",
        create_access_token(data={"sub": str(user.id), "role": user.role}),
    )


def add_listing(
    db_session: Session,
    landlord_id: int,
    *,
    title: str = "Campus apartment",
    city: str = "St. Augustine",
) -> Listing:
    listing = Listing(
        title=title,
        address="12 Campus Road",
        city=city,
        price_per_month=1500,
        property_type="Apartment",
        description="Near campus",
        landlord_id=landlord_id,
    )
    db_session.add(listing)
    db_session.commit()
    db_session.refresh(listing)
    return listing


def test_public_listing_list_search_and_detail(client, db_session, accounts):
    listing = add_listing(db_session, accounts["landlord"].id)

    response = client.get("/api/listings", params={"q": "St. Augustine"})

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == listing.id
    assert response.json()[0]["image_url"] is None

    detail = client.get(f"/api/listings/{listing.id}")
    assert detail.status_code == 200
    assert detail.json()["title"] == "Campus apartment"


def test_listing_detail_returns_404_for_missing_listing(client):
    response = client.get("/api/listings/999")

    assert response.status_code == 404


def test_listing_creation_requires_auth_and_records_owner(
    client,
    db_session,
    accounts,
):
    payload = {
        "title": "New student studio",
        "address": "4 College Road",
        "city": "St. Augustine",
        "price_per_month": 1700,
        "property_type": "Studio",
        "description": "Walking distance to campus",
    }

    denied = client.post("/api/listings", json=payload)
    assert denied.status_code == 401

    authenticate(client, accounts["landlord"])
    created = client.post("/api/listings", json=payload)

    assert created.status_code == 201
    assert created.json()["landlord_id"] == accounts["landlord"].id
    assert created.json()["title"] == payload["title"]

    owned = client.get("/api/me/listings")
    assert [row["id"] for row in owned.json()] == [created.json()["id"]]


def test_landlord_listing_collection_is_scoped_to_current_user(
    client,
    db_session,
    accounts,
):
    owned = add_listing(db_session, accounts["landlord"].id, title="Owned")
    add_listing(db_session, accounts["student"].id, title="Other user's listing")
    authenticate(client, accounts["landlord"])

    response = client.get("/api/me/listings")

    assert response.status_code == 200
    assert [row["id"] for row in response.json()] == [owned.id]


def test_booking_and_review_api_enforce_auth_and_booking_rule(
    client,
    db_session,
    accounts,
):
    listing = add_listing(db_session, accounts["landlord"].id)
    review_payload = {
        "listing_id": listing.id,
        "rating": 5,
        "comment": "Quiet and close to campus",
    }
    denied = client.post("/api/reviews", json=review_payload)
    assert denied.status_code == 401

    authenticate(client, accounts["student"])
    unavailable_review = client.post("/api/reviews", json=review_payload)
    assert unavailable_review.status_code == 403

    start_date = datetime.now(timezone.utc).date() + timedelta(days=30)
    booking = client.post(
        f"/api/listings/{listing.id}/bookings",
        json={
            "start_date": start_date.isoformat(),
            "end_date": (start_date + timedelta(days=30)).isoformat(),
        },
    )
    assert booking.status_code == 201
    assert booking.json()["student_id"] == accounts["student"].id
    assert booking.json()["total_price"] == 1500

    created_review = client.post("/api/reviews", json=review_payload)
    assert created_review.status_code == 201
    assert created_review.json()["student_id"] == accounts["student"].id

    listing_reviews = client.get(f"/api/listings/{listing.id}/reviews")
    assert listing_reviews.status_code == 200
    assert len(listing_reviews.json()) == 1

    my_bookings = client.get("/api/me/bookings")
    my_reviews = client.get("/api/me/reviews")
    assert len(my_bookings.json()) == 1
    assert len(my_reviews.json()) == 1


def test_booking_rejects_non_increasing_dates(client, db_session, accounts):
    listing = add_listing(db_session, accounts["landlord"].id)
    authenticate(client, accounts["student"])
    start_date = datetime.now(timezone.utc).date() + timedelta(days=30)

    response = client.post(
        f"/api/listings/{listing.id}/bookings",
        json={
            "start_date": start_date.isoformat(),
            "end_date": start_date.isoformat(),
        },
    )

    assert response.status_code == 422


def test_user_directory_api_is_admin_only(client, accounts):
    denied = client.get("/api/users")
    assert denied.status_code == 401

    authenticate(client, accounts["student"])
    forbidden = client.get("/api/users")
    assert forbidden.status_code == 403

    authenticate(client, accounts["admin"])
    allowed = client.get("/api/users")
    assert allowed.status_code == 200
    assert all("password" not in user for user in allowed.json())
