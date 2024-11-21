from http.client import responses
from typing import Annotated
from fastapi import APIRouter, status, Depends, Path, HTTPException
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from slugify import slugify

from sqlalchemy.ext.asyncio import AsyncSession

from backend.dp_depens import  get_db
from models.category import Category
from schemas.schemas import Category as category_create

router = APIRouter(prefix="/category", tags=['Categories'])

@router.get("/")
async def get_all_categories(db: Annotated[AsyncSession, Depends(get_db)]):
    categories = await db.scalars(select(Category).where(Category.is_active == True))
    return categories.all()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_category(db: Annotated[AsyncSession, Depends(get_db)],
                          create_category: category_create):
        await db.execute(insert(Category).values(
            name=create_category.name,
            parent_id=create_category.parent_id,
            slug=slugify(create_category.name))
        )
        await db.commit()

        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'
        }



@router.delete('/delete')
async def delete_category(db: Annotated[AsyncSession, Depends(get_db)], category_id: int):
    category = await db.scalar(select(Category).where(Category.id == category_id))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no category found'
        )
    await db.execute(update(Category).where(Category.id == category_id).values(is_active=False))
    await db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Category delete is successful'
    }

@router.put("/{category_id}",
               status_code=status.HTTP_200_OK,
               response_description="Запись успешно удалена")
async def delete_category(db: Annotated[AsyncSession, Depends(get_db)], category_id: Annotated[int, Path()]):
    category = await db.scalar(select(Category).where(Category.id == category_id))

    if category is None or category.is_active == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не нфйдена"
        )
    await db.execute(update(Category).where(Category.id == category_id).values(is_active=False))
    await db.commit()
    return {
        f"Категория '{category.name}' была успешно удалена!"
    }
