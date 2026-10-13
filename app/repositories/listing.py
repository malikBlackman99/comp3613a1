from __future__ import annotations

from typing import Optional

from sqlmodel import Session, select

from app.models.listing import Listing


class ListingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, listing: Listing) -> Listing:
        self.db.add(listing)
        self.db.commit()
        self.db.refresh(listing)
        return listing

    def get_all(self, query: str = "") -> list[Listing]:
        statement = select(Listing)
        if query:
            statement = statement.where(
                (Listing.title.ilike(f"%{query}%"))
                | (Listing.city.ilike(f"%{query}%"))
                | (Listing.address.ilike(f"%{query}%"))
            )
        return list(self.db.exec(statement.order_by(Listing.id)).all())

    def get_by_id(self, listing_id: int) -> Optional[Listing]:
        return self.db.get(Listing, listing_id)

    def get_by_landlord(self, landlord_id: int, query: str = "") -> list[Listing]:
        statement = select(Listing).where(Listing.landlord_id == landlord_id)
        if query:
            statement = statement.where(
                (Listing.title.ilike(f"%{query}%"))
                | (Listing.city.ilike(f"%{query}%"))
                | (Listing.address.ilike(f"%{query}%"))
            )
        return list(self.db.exec(statement.order_by(Listing.id)).all())

    def update(self, listing: Listing) -> Listing:
        self.db.add(listing)
        self.db.commit()
        self.db.refresh(listing)
        return listing
