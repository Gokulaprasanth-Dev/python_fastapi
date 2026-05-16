from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.services.dashboard_service import dashboard_summary

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("")
async def get_dashboard(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    result = await dashboard_summary(db)

    return result