from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from fastapi import APIRouter, Depends, HTTPException, status
from models.user import User

from backend.dp_depens import get_db
from .auth import get_current_user


router = APIRouter(prefix="/permission", tags=["Права доступа"])

@router.patch("/")
async def set_permission(db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[dict, Depends(get_current_user)],
                         user_id: int):
    if user.get("is_admin"):
        current_user = await db.scalar(select(User).where(User.id == user_id))
        if not current_user or current_user.is_active == False:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        if current_user.is_supplier:
            await db.execute(update(User).where(User.id == user_id).values(is_supplier=False, is_customer=True))
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail="User's premission has been updated!"
            )
        else:
            await db.execute(update(User).where(User.id == user_id).values(is_supplier=True, is_customer=False))
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail="User's premission has been updated!!"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You have not premission!"
        )


@router.delete("/delete/{user_id}")
async def delete_user(db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[dict, Depends(get_current_user)],
                         user_id: int):
    if user.get("is_admin"):
        current_user = await db.scalar(select(User).where(User.id == user_id))
        if current_user is None or not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You can't delete admin user"
            )

        await db.execute(update(User).where(User.id == user_id).values(is_active=False))
        await db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'detail': 'User is deleted'
        }
    return {
        "status": status.HTTP_401_UNAUTHORIZED,
        "detail": "You have not permission!"
    }