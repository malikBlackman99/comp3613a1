from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.listing import Listing
    from app.models.user import User


class BookingBase(SQLModel):
    student_id: int = Field(foreign_key="user.id", index=True)
    listing_id: int = Field(foreign_key="listing.id", index=True)
    start_date: date
    end_date: date
    status: str = Field(default="pending")
    total_price: float = Field(default=0.0, ge=0)


class Booking(BookingBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    student: Optional["User"] = Relationship(back_populates="bookings")
    listing: Optional["Listing"] = Relationship(back_populates="bookings")
