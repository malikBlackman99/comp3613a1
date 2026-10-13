from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.review import Review
    from app.models.user import User


class ListingBase(SQLModel):
    title: str = Field(index=True)
    address: str
    city: str = Field(index=True)
    price_per_month: float = Field(default=0.0, ge=0)
    property_type: str = Field(default="Apartment")
    status: str = Field(default="available")
    description: str = Field(default="")
    available: bool = True
    landlord_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Listing(ListingBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    landlord: Mapped["User"] = Relationship(back_populates="listings")
    bookings: Mapped[list["Booking"]] = Relationship(back_populates="listing")
    reviews: Mapped[list["Review"]] = Relationship(back_populates="listing")
