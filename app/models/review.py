from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.listing import Listing
    from app.models.user import User


class ReviewBase(SQLModel):
    student_id: int = Field(foreign_key="user.id", index=True)
    listing_id: int = Field(foreign_key="listing.id", index=True)
    rating: int = Field(default=5, ge=1, le=5)
    comment: str = Field(default="")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # === STUDENT: add created_at from the ERD (datetime, default now) ===
    # === END STUDENT ===


class Review(ReviewBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    student: Optional["User"] = Relationship(back_populates="reviews")
    listing: Optional["Listing"] = Relationship(back_populates="reviews")
