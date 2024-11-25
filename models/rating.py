from sqlalchemy.orm import relationship

from backend.db import Base
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean, Float


class Rating(Base):
    __tablename__ = "rating"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    grade = Column(Float)
    is_active = Column(Boolean, default=True)

    review = relationship("Review", uselist=False, back_populates="rating")
    product = relationship("Product", back_populates="ratings")
