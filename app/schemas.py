from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=160)
    isbn: str | None = Field(default=None, max_length=20)
    copies: int = Field(default=1, ge=1)


class BookOut(BookCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    available_copies: int


class ReaderCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=160)
    email: EmailStr


class ReaderOut(ReaderCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class LoanCreate(BaseModel):
    book_id: int = Field(gt=0)
    reader_id: int = Field(gt=0)
    due_date: date


class LoanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    book_id: int
    reader_id: int
    borrowed_at: date
    due_date: date
    returned_at: date | None
