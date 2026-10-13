from __future__ import annotations

from sqlmodel import Session, select

from app.models.review import Review


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, review: Review) -> Review:
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def get_for_listing(self, listing_id: int) -> list[Review]:
        return self.db.exec(
            select(Review).where(Review.listing_id == listing_id).order_by(Review.id)
        ).all()

    def get_for_student(self, student_id: int) -> list[Review]:
        return self.db.exec(
            select(Review).where(Review.student_id == student_id).order_by(Review.id)
        ).all()
