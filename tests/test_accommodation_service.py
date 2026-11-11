from datetime import date
from unittest.mock import Mock

import pytest

from app.models.booking import Booking
from app.models.listing import Listing
from app.models.review import Review
from app.repositories.booking import BookingRepository
from app.repositories.listing import ListingRepository
from app.repositories.review import ReviewRepository
from app.services.accommodation_service import AccommodationService


def make_listing(listing_id: int = 1, price: float = 1200.0) -> Listing:
    return Listing(
        id=listing_id,
        title="Campus apartment",
        address="12 Campus Road",
        city="St. Augustine",
        price_per_month=price,
        property_type="Apartment",
        landlord_id=4,
    )


@pytest.fixture
def service():
    listing_repository = Mock(spec=ListingRepository)
    booking_repository = Mock(spec=BookingRepository)
    review_repository = Mock(spec=ReviewRepository)
    return AccommodationService(
        listing_repository,
        booking_repository,
        review_repository,
    ), listing_repository, booking_repository, review_repository


def test_create_listing_normalizes_input_and_sets_owner(service):
    accommodation, listing_repository, _, _ = service
    listing_repository.create.side_effect = lambda listing: listing

    listing = accommodation.create_listing(
        9,
        title="  Campus apartment ",
        address=" 12 Campus Road ",
        city=" St. Augustine ",
        price_per_month=1200,
        property_type=" ",
        description="  Near campus ",
        listingImg=" https://example.test/flat.png ",
    )

    assert listing.title == "Campus apartment"
    assert listing.address == "12 Campus Road"
    assert listing.city == "St. Augustine"
    assert listing.property_type == "Apartment"
    assert listing.description == "Near campus"
    assert listing.listingImg == "https://example.test/flat.png"
    assert listing.landlord_id == 9
    assert listing.available is True
    listing_repository.create.assert_called_once()


def test_create_booking_calculates_monthly_total(service):
    accommodation, listing_repository, booking_repository, _ = service
    listing_repository.get_by_id.return_value = make_listing(price=1500)
    booking_repository.create.side_effect = lambda booking: booking

    booking = accommodation.create_booking(
        7,
        1,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
    )

    assert booking.student_id == 7
    assert booking.listing_id == 1
    assert booking.status == "pending"
    assert booking.total_price == 1500


def test_create_booking_rejects_non_positive_date_range(service):
    accommodation, listing_repository, booking_repository, _ = service

    with pytest.raises(ValueError, match="End date must be after start date"):
        accommodation.create_booking(
            7,
            1,
            start_date=date(2026, 2, 1),
            end_date=date(2026, 2, 1),
        )

    listing_repository.get_by_id.assert_not_called()
    booking_repository.create.assert_not_called()


def test_create_review_requires_a_previous_booking(service):
    accommodation, listing_repository, booking_repository, review_repository = service
    listing_repository.get_by_id.return_value = make_listing()
    booking_repository.get_for_student.return_value = []

    with pytest.raises(PermissionError, match="previous booking"):
        accommodation.create_review(7, 1, rating=5, comment="Great")

    review_repository.create.assert_not_called()


def test_create_review_trims_comment_for_a_booked_listing(service):
    accommodation, listing_repository, booking_repository, review_repository = service
    listing_repository.get_by_id.return_value = make_listing()
    booking_repository.get_for_student.return_value = [
        Booking(student_id=7, listing_id=1, start_date=date(2026, 1, 1), end_date=date(2026, 2, 1))
    ]
    review_repository.create.side_effect = lambda review: review

    review = accommodation.create_review(7, 1, rating=4, comment="  Clean and quiet  ")

    assert review.rating == 4
    assert review.comment == "Clean and quiet"
    assert review.student_id == 7
    assert review.listing_id == 1


def test_landlord_average_rating_uses_reviews_across_owned_listings(service):
    accommodation, listing_repository, _, review_repository = service
    listing_repository.get_by_landlord.return_value = [
        make_listing(1),
        make_listing(2),
    ]
    review_repository.get_for_listing.side_effect = [
        [Review(student_id=1, listing_id=1, rating=4, comment="Good")],
        [
            Review(student_id=2, listing_id=2, rating=2, comment="Okay"),
            Review(student_id=3, listing_id=2, rating=5, comment="Great"),
        ],
    ]

    assert accommodation.landlord_average_rating(4) == pytest.approx(11 / 3)


def test_landlord_average_rating_is_none_without_reviews(service):
    accommodation, listing_repository, _, review_repository = service
    listing_repository.get_by_landlord.return_value = [make_listing()]
    review_repository.get_for_listing.return_value = []

    assert accommodation.landlord_average_rating(4) is None
