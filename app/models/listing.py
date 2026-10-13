from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

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
    # === STUDENT: add image_url field here (text/url, optional default) ===
    listingImg: Optional[str] = Field(default=None)
    # === END STUDENT ===


class Listing(ListingBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    landlord: Optional["User"] = Relationship(back_populates="listings")
    bookings: List["Booking"] = Relationship(back_populates="listing")
    reviews: List["Review"] = Relationship(back_populates="listing")
