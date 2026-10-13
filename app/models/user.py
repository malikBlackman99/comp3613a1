from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from pydantic import EmailStr
from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.listing import Listing
    from app.models.review import Review


class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: EmailStr = Field(index=True, unique=True)
    password: str
    role: str = ""


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    listings: Mapped[list["Listing"]] = Relationship(back_populates="landlord")
    bookings: Mapped[list["Booking"]] = Relationship(back_populates="student")
    reviews: Mapped[list["Review"]] = Relationship(back_populates="student")
