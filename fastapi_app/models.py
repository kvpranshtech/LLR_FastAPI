# fastapi_app/models.py
from sqlalchemy import Column, Integer, String, Date, Numeric

from djproject.database import Base


class Book(Base):
    __tablename__ = "book"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    author = Column(String(100))
    published = Column(Date)
    price = Column(Numeric(8, 2))
