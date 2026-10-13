from __future__ import annotations

from sqlmodel import Session, select

from app.models.booking import Booking


class BookingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, booking: Booking) -> Booking:
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def get_for_listing(self, listing_id: int) -> list[Booking]:
        return self.db.exec(
            select(Booking).where(Booking.listing_id == listing_id).order_by(Booking.id)
        ).all()

    def get_for_student(self, student_id: int) -> list[Booking]:
        return self.db.exec(
            select(Booking).where(Booking.student_id == student_id).order_by(Booking.id)
        ).all()
