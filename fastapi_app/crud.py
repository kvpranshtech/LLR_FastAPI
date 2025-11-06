# fastapi_app/crud.py
from sqlalchemy.orm import Session

from djproject import models
from fastapi_app import schemas


def get_books(db: Session):
    return db.query(models.Book).all()


def create_book(db: Session, book: schemas.BookCreate):
    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book
