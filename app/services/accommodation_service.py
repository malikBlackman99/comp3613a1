from __future__ import annotations

from datetime import date
from typing import Optional

from app.models.booking import Booking
from app.models.listing import Listing
from app.models.review import Review
from app.repositories.booking import BookingRepository
from app.repositories.listing import ListingRepository
from app.repositories.review import ReviewRepository


class AccommodationService:
    def __init__(
        self,
        listing_repository: ListingRepository,
        booking_repository: Optional[BookingRepository] = None,
        review_repository: Optional[ReviewRepository] = None,
    ):
        self.listing_repository = listing_repository
        self.booking_repository = booking_repository or BookingRepository(listing_repository.db)
        self.review_repository = review_repository or ReviewRepository(listing_repository.db)

    def list_listings(self, query: str = "") -> list[Listing]:
        return self.listing_repository.get_all(query=query)

    def get_listing(self, listing_id: int) -> Optional[Listing]:
        return self.listing_repository.get_by_id(listing_id)

    def create_listing(
        self,
        landlord_id: int,
        *,
        title: str,
        address: str,
        city: str,
        price_per_month: float,
        property_type: str,
        description: str,
        listingImg: Optional[str] = None,
    ) -> Listing:
        listing = Listing(
            title=title.strip(),
            address=address.strip(),
            city=city.strip(),
            price_per_month=float(price_per_month),
            property_type=property_type.strip() or "Apartment",
            description=description.strip(),
            available=True,
            status="available",
            landlord_id=landlord_id,
            listingImg=(listingImg or "").strip() or None,
        )
        return self.listing_repository.create(listing)

    def create_booking(
        self,
        student_id: int,
        listing_id: int,
        *,
        start_date: date,
        end_date: date,
    ) -> Booking:
        listing = self.get_listing(listing_id)
        if listing is None:
            raise ValueError("Listing does not exist")
        total_price = float(listing.price_per_month) * max((end_date - start_date).days / 30, 1)
        booking = Booking(
            student_id=student_id,
            listing_id=listing_id,
            start_date=start_date,
            end_date=end_date,
            status="pending",
            total_price=round(total_price, 2),
        )
        return self.booking_repository.create(booking)

    def create_review(
        self,
        student_id: int,
        listing_id: int,
        *,
        rating: int,
        comment: str,
    ) -> Review:
        review = Review(
            student_id=student_id,
            listing_id=listing_id,
            rating=int(rating),
            comment=comment.strip(),
        )
        return self.review_repository.create(review)

    def get_reviews_for_listing(self, listing_id: int) -> list[Review]:
        return self.review_repository.get_for_listing(listing_id)

    def get_user_listings(self, landlord_id: int, query: str = "") -> list[Listing]:
        return self.listing_repository.get_by_landlord(landlord_id, query=query)

    def get_booked_listings(self, student_id: int) -> list[Listing]:
        # === STUDENT: return only listings this student has booked ===
        # 1. Get the student's bookings via self.booking_repository
        booking = self.booking_repository.get_for_student(student_id)
        # 2. Collect unique listing_ids (a student may book the same listing once)
        listing_ids = {booking.listing_id for booking in booking}
        
        # 3. Return the Listing rows for those ids (get_listing is fine to reuse)
        return [listing for listing_id in listing_ids if (listing := self.get_listing(listing_id)) is not None]
        # No raw SQL.
        
        # === END STUDENT ===

    def landlord_average_rating(self, landlord_id: int) -> float | None:
        listings = self.get_user_listings(landlord_id)
        ratings: list[int] = []
        for listing in listings:
            reviews = self.review_repository.get_for_listing(listing.id)
            # === STUDENT: extend ratings with each review's rating ===
            ratings.extend([review.rating for review in reviews])
            # === END STUDENT ===
        if not ratings:
            return None
        # === STUDENT: return the average of ratings ===
        return sum(ratings) / len(ratings)
        # === END STUDENT ===
