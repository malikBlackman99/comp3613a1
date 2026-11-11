from datetime import date, datetime

from pydantic import ConfigDict, model_validator
from sqlmodel import Field, SQLModel


class ListingCreate(SQLModel):
    title: str = Field(min_length=1, max_length=160)
    address: str = Field(min_length=1, max_length=240)
    city: str = Field(min_length=1, max_length=120)
    price_per_month: float = Field(ge=0)
    property_type: str = Field(default="Apartment", min_length=1, max_length=80)
    description: str = Field(default="", max_length=4000)
    image_url: str | None = Field(default=None, max_length=2000)


class ListingRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    address: str
    city: str
    price_per_month: float
    property_type: str
    status: str
    description: str
    available: bool
    landlord_id: int
    created_at: datetime
    image_url: str | None = Field(default=None, validation_alias="listingImg")


class BookingCreate(SQLModel):
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_date_range(self) -> "BookingCreate":
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class BookingRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    listing_id: int
    start_date: date
    end_date: date
    status: str
    total_price: float


class ReviewCreate(SQLModel):
    listing_id: int
    rating: int = Field(ge=1, le=5)
    comment: str = Field(min_length=1, max_length=4000)


class ReviewRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    listing_id: int
    rating: int
    comment: str
    created_at: datetime
