from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean
from datetime import datetime

from sqlalchemy.orm import relationship

from backend.db import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    rating_id = Column(Integer, ForeignKey("rating.id"))
    comment = Column(String)
    comment_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    rating = relationship("Rating", back_populates="review")
    product = relationship("Product", back_populates="review")


