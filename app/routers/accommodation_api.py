from fastapi import APIRouter, HTTPException, Query, status

from app.dependencies import SessionDep
from app.dependencies.auth import AuthDep
from app.repositories.listing import ListingRepository
from app.schemas.accommodation import (
    BookingCreate,
    BookingRead,
    ListingCreate,
    ListingRead,
    ReviewCreate,
    ReviewRead,
)
from app.services.accommodation_service import AccommodationService

accommodation_api_router = APIRouter(tags=["Accommodation API"])


@accommodation_api_router.get("/listings", response_model=list[ListingRead])
async def list_listings(
    db: SessionDep,
    q: str = Query(default="", max_length=120),
):
    return AccommodationService(ListingRepository(db)).list_listings(query=q)


@accommodation_api_router.get(
    "/listings/{listing_id}",
    response_model=ListingRead,
)
async def get_listing(listing_id: int, db: SessionDep):
    listing = AccommodationService(ListingRepository(db)).get_listing(listing_id)
    if listing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found",
        )
    return listing


@accommodation_api_router.get(
    "/listings/{listing_id}/reviews",
    response_model=list[ReviewRead],
)
async def list_listing_reviews(listing_id: int, db: SessionDep):
    service = AccommodationService(ListingRepository(db))
    if service.get_listing(listing_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found",
        )
    return service.get_reviews_for_listing(listing_id)


@accommodation_api_router.post(
    "/listings",
    response_model=ListingRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_listing(
    payload: ListingCreate,
    db: SessionDep,
    user: AuthDep,
):
    return AccommodationService(ListingRepository(db)).create_listing(
        user.id,
        title=payload.title,
        address=payload.address,
        city=payload.city,
        price_per_month=payload.price_per_month,
        property_type=payload.property_type,
        description=payload.description,
        listingImg=payload.image_url,
    )


@accommodation_api_router.get(
    "/me/listings",
    response_model=list[ListingRead],
)
async def list_my_listings(
    db: SessionDep,
    user: AuthDep,
    q: str = Query(default="", max_length=120),
):
    return AccommodationService(ListingRepository(db)).get_user_listings(
        user.id,
        query=q,
    )


@accommodation_api_router.post(
    "/listings/{listing_id}/bookings",
    response_model=BookingRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_booking(
    listing_id: int,
    payload: BookingCreate,
    db: SessionDep,
    user: AuthDep,
):
    service = AccommodationService(ListingRepository(db))
    if service.get_listing(listing_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found",
        )
    return service.create_booking(
        user.id,
        listing_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )


@accommodation_api_router.get(
    "/me/bookings",
    response_model=list[BookingRead],
)
async def list_my_bookings(db: SessionDep, user: AuthDep):
    return AccommodationService(ListingRepository(db)).get_bookings_for_student(
        user.id
    )


@accommodation_api_router.post(
    "/reviews",
    response_model=ReviewRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_review(
    payload: ReviewCreate,
    db: SessionDep,
    user: AuthDep,
):
    service = AccommodationService(ListingRepository(db))
    try:
        return service.create_review(
            user.id,
            payload.listing_id,
            rating=payload.rating,
            comment=payload.comment,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@accommodation_api_router.get(
    "/me/reviews",
    response_model=list[ReviewRead],
)
async def list_my_reviews(db: SessionDep, user: AuthDep):
    return AccommodationService(ListingRepository(db)).get_reviews_for_student(
        user.id
    )
