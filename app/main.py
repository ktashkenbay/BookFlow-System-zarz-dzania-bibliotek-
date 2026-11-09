from datetime import date

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Book, Loan, Reader
from app.schemas import BookCreate, BookOut, LoanCreate, LoanOut, ReaderCreate, ReaderOut

Base.metadata.create_all(bind=engine)
app = FastAPI(title="BookFlow API", description="Podstawowe zarządzanie biblioteką.", version="1.0.0")


def _available_copies(db: Session, book: Book) -> int:
    active_loans = db.scalar(
        select(func.count(Loan.id)).where(Loan.book_id == book.id, Loan.returned_at.is_(None))
    ) or 0
    return book.copies - active_loans


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/books", response_model=BookOut, status_code=status.HTTP_201_CREATED)
def create_book(payload: BookCreate, db: Session = Depends(get_db)) -> BookOut:
    book = Book(**payload.model_dump())
    db.add(book)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Książka o podanym ISBN już istnieje.") from exc
    db.refresh(book)
    return BookOut(**BookCreate.model_validate(book).model_dump(), id=book.id, available_copies=book.copies)


@app.get("/books", response_model=list[BookOut])
def list_books(db: Session = Depends(get_db)) -> list[BookOut]:
    books = db.scalars(select(Book).order_by(Book.title)).all()
    return [
        BookOut(
            id=book.id,
            title=book.title,
            author=book.author,
            isbn=book.isbn,
            copies=book.copies,
            available_copies=_available_copies(db, book),
        )
        for book in books
    ]


@app.post("/readers", response_model=ReaderOut, status_code=status.HTTP_201_CREATED)
def create_reader(payload: ReaderCreate, db: Session = Depends(get_db)) -> Reader:
    reader = Reader(**payload.model_dump())
    db.add(reader)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Czytelnik o podanym adresie e-mail już istnieje.") from exc
    db.refresh(reader)
    return reader


@app.get("/readers", response_model=list[ReaderOut])
def list_readers(db: Session = Depends(get_db)) -> list[Reader]:
    return list(db.scalars(select(Reader).order_by(Reader.full_name)).all())


@app.post("/loans", response_model=LoanOut, status_code=status.HTTP_201_CREATED)
def create_loan(payload: LoanCreate, db: Session = Depends(get_db)) -> Loan:
    today = date.today()
    if payload.due_date <= today:
        raise HTTPException(status_code=422, detail="Termin zwrotu musi przypadać po dzisiejszej dacie.")

    book = db.get(Book, payload.book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Nie znaleziono książki.")
    if db.get(Reader, payload.reader_id) is None:
        raise HTTPException(status_code=404, detail="Nie znaleziono czytelnika.")
    if _available_copies(db, book) < 1:
        raise HTTPException(status_code=409, detail="Brak dostępnych egzemplarzy.")

    loan = Loan(book_id=book.id, reader_id=payload.reader_id, borrowed_at=today, due_date=payload.due_date)
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


@app.get("/loans/active", response_model=list[LoanOut])
def list_active_loans(db: Session = Depends(get_db)) -> list[Loan]:
    return list(
        db.scalars(
            select(Loan).where(Loan.returned_at.is_(None)).order_by(Loan.due_date, Loan.id)
        ).all()
    )


@app.post("/loans/{loan_id}/return", response_model=LoanOut)
def return_loan(loan_id: int, db: Session = Depends(get_db)) -> Loan:
    loan = db.get(Loan, loan_id)
    if loan is None:
        raise HTTPException(status_code=404, detail="Nie znaleziono wypożyczenia.")
    if loan.returned_at is not None:
        raise HTTPException(status_code=409, detail="To wypożyczenie zostało już zwrócone.")
    loan.returned_at = date.today()
    db.commit()
    db.refresh(loan)
    return loan
