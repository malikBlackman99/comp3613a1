from __future__ import annotations

from datetime import date

from fastapi import Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.dependencies import SessionDep
from app.dependencies.auth import AuthDep, OptionalUser
from app.repositories.listing import ListingRepository
from app.repositories.review import ReviewRepository
from app.repositories.user import UserRepository
from app.services.accommodation_service import AccommodationService
from app.utilities.flash import flash
from . import router, templates


@router.get("/listings", response_class=HTMLResponse, name="listings_view")
async def listings_view(
    request: Request,
    db: SessionDep,
    user: OptionalUser,
    q: str | None = None,
):
    query = q or ""
    # === STUDENT: complete the listings_view handler ===
    listings = AccommodationService(ListingRepository(db))
    listings = listings.list_listings(query=query)
    # === END STUDENT ===
    return templates.TemplateResponse(
        request=request,
        name="listings.html",
        context={
            "user": user,
            "listings": listings,
            "query": query,
        },
    )


@router.get("/listings/{listing_id}", response_class=HTMLResponse, name="listing_detail_view")
async def listing_detail_view(
    request: Request,
    db: SessionDep,
    user: OptionalUser,
    listing_id: int,
):
    repo = ListingRepository(db)
    service = AccommodationService(repo)
    listing = service.get_listing(listing_id)
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    reviews = service.get_reviews_for_listing(listing_id)
    return templates.TemplateResponse(
        request=request,
        name="listing_detail.html",
        context={
            "user": user,
            "listing": listing,
            "reviews": reviews,
        },
    )


@router.post("/listings/{listing_id}/book", response_class=HTMLResponse, name="book_listing")
async def book_listing(
    request: Request,
    db: SessionDep,
    user: AuthDep,
    listing_id: int,
    start_date: str = Form(...),
    end_date: str = Form(...),
):
    repo = ListingRepository(db)
    service = AccommodationService(repo)
    try:
        service.create_booking(
            user.id,
            listing_id,
            start_date=date.fromisoformat(start_date),
            end_date=date.fromisoformat(end_date),
        )
        flash(request, "Booking request saved!", "success")
    except ValueError as exc:
        flash(request, str(exc), "danger")
    except Exception:
        flash(request, "Unable to create booking right now.", "danger")
    return RedirectResponse(url=request.url_for("listing_detail_view", listing_id=listing_id), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/reviews", response_class=HTMLResponse, name="reviews_view")
async def reviews_view(
    request: Request,
    db: SessionDep,
    user: AuthDep,
):
    repo = ListingRepository(db)
    service = AccommodationService(repo)
    listings = service.list_listings(query="")
    review_repo = ReviewRepository(db)
    user_reviews = review_repo.get_for_student(user.id)
    return templates.TemplateResponse(
        request=request,
        name="reviews.html",
        context={
            "user": user,
            "listings": listings,
            "user_reviews": user_reviews,
        },
    )


@router.post("/reviews", response_class=HTMLResponse, name="submit_review")
async def submit_review(
    request: Request,
    db: SessionDep,
    user: AuthDep,
    listing_id: int = Form(...),
    rating: int = Form(...),
    comment: str = Form(...),
):
    repo = ListingRepository(db)
    service = AccommodationService(repo)
    try:
        service.create_review(user.id, listing_id, rating=rating, comment=comment)
        flash(request, "Review submitted successfully.", "success")
    except Exception:
        flash(request, "Review could not be saved.", "danger")
    return RedirectResponse(url=request.url_for("reviews_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/manage-listings", response_class=HTMLResponse, name="manage_listings_view")
async def manage_listings_view(
    request: Request,
    db: SessionDep,
    user: AuthDep,
):
    repo = ListingRepository(db)
    service = AccommodationService(repo)
    listings = service.get_user_listings(user.id)
    return templates.TemplateResponse(
        request=request,
        name="manage_listings.html",
        context={
            "user": user,
            "listings": listings,
        },
    )


@router.post("/manage-listings", response_class=HTMLResponse, name="create_listing")
async def create_listing(
    request: Request,
    db: SessionDep,
    user: AuthDep,
    title: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    price_per_month: float = Form(...),
    property_type: str = Form(...),
    description: str = Form(default=""),
):
    repo = ListingRepository(db)
    service = AccommodationService(repo)
    try:
        service.create_listing(
            user.id,
            title=title,
            address=address,
            city=city,
            price_per_month=price_per_month,
            property_type=property_type,
            description=description,
        )
        flash(request, "Listing published.", "success")
    except Exception:
        flash(request, "Listing could not be created.", "danger")
    return RedirectResponse(url=request.url_for("manage_listings_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/profile", response_class=HTMLResponse, name="profile_view")
async def profile_view(
    request: Request,
    db: SessionDep,
    user: AuthDep,
):
    repo = ListingRepository(db)
    service = AccommodationService(repo)
    listings = service.get_user_listings(user.id)
    review_repo = ReviewRepository(db)
    user_reviews = review_repo.get_for_student(user.id)
    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={
            "user": user,
            "listings": listings,
            "user_reviews": user_reviews,
        },
    )
