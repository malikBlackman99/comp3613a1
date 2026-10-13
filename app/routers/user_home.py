from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi import status
from app.dependencies.auth import AuthDep
from . import router


@router.get("/app", response_class=RedirectResponse)
async def user_home_view(
    request: Request,
    user: AuthDep,
):
    return RedirectResponse(
        url=request.url_for("listings_view"),
        status_code=status.HTTP_303_SEE_OTHER,
    )