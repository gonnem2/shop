from sqlalchemy import Column, ForeignKey, Integer, String, Boolean

from sqlalchemy.orm import mapped_column, relationship

from backend.db import Base
from  models.product import Product


class Category(Base):
    __tablename__ = "category"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    slug = Column(String, unique=True, index=True)
    parent_id = Column(Integer, ForeignKey('category.id'), nullable=True)
    is_active = Column(Boolean, default=True)



    product = relationship("Product", back_populates="category")

