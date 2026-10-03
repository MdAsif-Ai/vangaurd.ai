"""Financial analysis API (placeholders).

The deterministic financial calculation engine is planned for a later
phase; these endpoints intentionally return 501 instead of fake results.
"""

from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import CurrentUser

router = APIRouter()

_FINANCIAL_NOT_IMPLEMENTED = (
    "Financial analysis is planned for a later phase "
    "(deterministic calculation engine over verified financial facts)."
)
_COMPARE_NOT_IMPLEMENTED = (
    "Cross-document/company comparison is planned for a later phase "
    "(multi-document retrieval plus deterministic calculations)."
)


@router.post("/financial")
async def financial_analysis(current_user: CurrentUser) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=_FINANCIAL_NOT_IMPLEMENTED
    )


@router.post("/compare")
async def compare_analysis(current_user: CurrentUser) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=_COMPARE_NOT_IMPLEMENTED
    )
