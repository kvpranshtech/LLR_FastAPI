from pydantic import BaseModel
from datetime import datetime


class BookCreate(BaseModel):
    title: str
    author_id: int  # use id, not name
    pages: int


class BookRead(BaseModel):
    id: int
    title: str
    author: str  # this will show author name
    pages: int
    created_at: datetime

    class Config:
        from_attributes = True
