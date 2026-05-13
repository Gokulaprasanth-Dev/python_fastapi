from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from database import Base


class Product(Base):

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    price = Column(Float, nullable=False)

    category = Column(String, nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)