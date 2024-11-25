from itertools import product
from typing import Annotated
from unicodedata import category

from fastapi import APIRouter, Depends, Body, status, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete
from slugify import slugify

from backend.dp_depens import get_db
from schemas.schemas import Product
from models.product import Product as product_db
from models.category import Category

from .auth import get_current_user


router = APIRouter(prefix="/products", tags=['Products'])


@router.get('/')
async def all_products(db: Annotated[AsyncSession, Depends(get_db)]):
    products = await db.scalars(select(product_db).where(product_db.is_active == True, product_db.stock > 0))
    product = products.all()
    if len(product) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There are no product"
        )

    return product

@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_product(db: Annotated[AsyncSession, Depends(get_db)], product: Annotated[Product, Body()], current_user: Annotated[dict, Depends(get_current_user)]):
    if current_user.get("is_customer"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You have not permission!"
        )

    product = await db.execute(insert(product_db).values(
        name=product.name,
        description=product.description,
        price=product.price,
        image_url=product.image_url,
        stock=product.stock,
        category_id=product.category,
        slug= slugify(product.name),
        rating=product.rating,
        supplier_id=current_user.get('id'),

    ))
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.get('/{category_slug}')
async def product_by_category(category_slug: Annotated[int, Path()], db: Annotated[AsyncSession, Depends(get_db)]):
    category = await db.scalar(select(Category).where(Category.id == category_slug))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    subcategories = await db.scalars(select(Category.id).where(Category.parent_id == category.id))

    category_ids = [category.id] + subcategories.all()

    products = await db.scalars(
        select(product_db).where(
            product_db.category_id.in_(category_ids),
            product_db.is_active == True,
            product_db.stock > 0
        )
    )

    return products.all()


@router.get('/detail/{product_slug}')
async def product_detail(product_slug: int, db: Annotated[AsyncSession, Depends(get_db)]):
    products = await db.scalar(select(product_db).where(product_db.id == product_slug))
    if products is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There are no product"
        )

    return products



@router.put('/detail/{product_slug}')
async def update_product(
        product_slug: int,
        db: Annotated[AsyncSession, Depends(get_db)],
        product: Annotated[Product, Body()],
        current_user: Annotated[dict, Depends(get_current_user)]
):

    if current_user.get("is_customer"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You have not permission!"
        )
    existing_product = await db.scalar(
        select(product_db).where(product_db.id == product_slug)
    )
    if existing_product.supplier_id != current_user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Не ваш товар!"
        )
    if existing_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    await db.execute(
        update(product_db)
        .where(product_db.id == product_slug)
        .values(
            name=product.name,
            description=product.description,
            price=product.price,
            image_url=product.image_url,
            stock=product.stock,
            category_id=product.category,
            slug=slugify(product.name),
            rating=product.rating))
    await db.commit()

    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Product update is successful'
            }

@router.delete('/delete')
async def delete_product(product_id: int, db: Annotated[AsyncSession, Depends(get_db)], current_user: Annotated[dict, Depends(get_current_user)]):
    if current_user.get("is_customer"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You have not permission!"
        )
    existing_product = await db.scalar(select(product_db).where(product_db.id == product_id))
    if existing_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There is no product found"
        )

    if existing_product.supplier_id != current_user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Не ваш товар!"
        )

    await db.execute(delete(product_db).where(product_db.id == product_id))
    await db.commit()

    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Product delete is successful'
    }
