
from typing import Annotated
from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy import insert, select, update

from sqlalchemy.orm import selectinload

from sqlalchemy.ext.asyncio import AsyncSession

from backend.dp_depens import get_db
from schemas.schemas import CreateReview
from models.review import Review
from models.rating import Rating
from .auth import get_current_user



router = APIRouter(prefix="/review", tags=['Review'])


@router.post("/create/{product_id}")
async def create_review(db: Annotated[AsyncSession, Depends(get_db)],
                        review: CreateReview,
                        user: Annotated[dict, Depends(get_current_user)],
                        product_id: int
                        ):
    rating = await db.execute(insert(Rating).values(user_id=user.get("id"),
                                           product_id=product_id,
                                           grade=review.grade,
                                           ).returning(Rating.id)
                              )
    rating_id = rating.scalar()
    review = await db.execute(insert(Review).values(
        user_id = user.get("id"),
        product_id=product_id,
        rating_id=rating_id,
        comment=review.comment,
    ))
    await db.commit()
    return {
        "status_code": status.HTTP_201_CREATED,
        "detail": "review has been added"
    }


@router.get("/all_reviews", status_code=status.HTTP_200_OK)
async def get_all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    reviews = await db.scalars(select(Review).where(Review.is_active != False).options(selectinload(Review.rating)))
    reviews = reviews.all()
    if len(reviews) == 0:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reviews not Found"
        )
    return reviews

@router.get("/product_reviews", status_code=status.HTTP_200_OK)
async def get_all_reviews(db: Annotated[AsyncSession, Depends(get_db)], product_id: Annotated[int, Query()]):
    reviews = await db.scalars(select(Review)
                               .where(Review.product_id == product_id, Review.is_active != False).
                               options(selectinload(Review.rating)))
    reviews = reviews.all()
    if len(reviews) == 0:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not Found"
        )
    return reviews

@router.delete("/delete/{review_id}")
async def delete_review(db: Annotated[AsyncSession, Depends(get_db)], review_id: int, current_user: Annotated[dict, Depends(get_current_user)]):
    if current_user.get("is_admin"):
        await db.execute(update(Review).values(is_active = False))
        await db.execute(update(Rating).values(is_active = False))
        await db.commit()
        return {
            "status_code": status.HTTP_200_OK,
            "detail": "Review's has been removed!"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You have not permission!"
        )