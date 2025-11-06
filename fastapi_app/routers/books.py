from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from typing import List
from django.forms.models import model_to_dict

# Import Django models safely (setup already done in main.py)
from djproject.models import Book

from fastapi_app.schemas import BookCreate, BookRead

router = APIRouter(prefix="/books", tags=["Books"])

def serialize(book: Book) -> BookRead:
    data = model_to_dict(book)
    return BookRead(**data)

@router.get("/", response_model=List[BookRead])
async def list_books():
    def _query():
        return [serialize(b) for b in Book.objects.all()]
    return await run_in_threadpool(_query)

@router.post("/", response_model=BookRead, status_code=201)
async def create_book(book: BookCreate):
    def _create():
        new_book = Book.objects.create(**book.dict())
        return serialize(new_book)
    return await run_in_threadpool(_create)

@router.get("/{book_id}", response_model=BookRead)
async def get_book(book_id: int):
    def _get():
        try:
            return serialize(Book.objects.get(id=book_id))
        except Book.DoesNotExist:
            return None
    book = await run_in_threadpool(_get)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book
