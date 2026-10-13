from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.listing import Listing
    from app.models.user import User


class ReviewBase(SQLModel):
    student_id: int = Field(foreign_key="user.id", index=True)
    listing_id: int = Field(foreign_key="listing.id", index=True)
    rating: int = Field(default=5, ge=1, le=5)
    comment: str = Field(default="")


class Review(ReviewBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    student: Mapped["User"] = Relationship(back_populates="reviews")
    listing: Mapped["Listing"] = Relationship(back_populates="reviews")
