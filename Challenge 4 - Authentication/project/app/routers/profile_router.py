from fastapi import APIRouter, Depends

from app.dependencies import get_current_user

router = APIRouter()


@router.get("/profile")
def get_profile(user=Depends(get_current_user)):

    return {
        "username": user.get("sub"),
        "role": user.get("role")
    }
