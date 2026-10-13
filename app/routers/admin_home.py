from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi import status
from app.dependencies.auth import AdminDep
from . import router


@router.get("/admin", response_class=RedirectResponse)
async def admin_home_view(
    request: Request,
    user: AdminDep,
):
    return RedirectResponse(
        url=request.url_for("listings_view"),
        status_code=status.HTTP_303_SEE_OTHER,
    )
