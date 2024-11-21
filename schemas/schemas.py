from typing import Optional

from pydantic import BaseModel

class Product(BaseModel):
    name: str
    description: str
    price: float
    image_url: str
    stock: int
    category: int
    rating: float


class Category(BaseModel):
    name: str
    parent_id: Optional[int]

class CreateUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str