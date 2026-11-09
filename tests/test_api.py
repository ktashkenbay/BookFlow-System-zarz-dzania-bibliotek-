from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


def test_catalog_and_checkout_return_flow(client):
    book = client.post("/books", json={"title": "Solaris", "author": "Stanisław Lem", "copies": 1})
    reader = client.post("/readers", json={"full_name": "Jan Kowalski", "email": "jan@example.com"})
    assert book.status_code == 201
    assert reader.status_code == 201

    loan = client.post(
        "/loans",
        json={
            "book_id": book.json()["id"],
            "reader_id": reader.json()["id"],
            "due_date": (date.today() + timedelta(days=14)).isoformat(),
        },
    )
    assert loan.status_code == 201
    assert client.get("/books").json()[0]["available_copies"] == 0
    assert len(client.get("/loans/active").json()) == 1

    returned = client.post(f"/loans/{loan.json()['id']}/return")
    assert returned.status_code == 200
    assert returned.json()["returned_at"] == date.today().isoformat()
    assert client.get("/books").json()[0]["available_copies"] == 1
    assert client.get("/loans/active").json() == []


def test_cannot_borrow_when_no_copies_are_available(client):
    book = client.post("/books", json={"title": "Solaris", "author": "Stanisław Lem"}).json()
    reader = client.post("/readers", json={"full_name": "Jan Kowalski", "email": "jan@example.com"}).json()
    payload = {
        "book_id": book["id"],
        "reader_id": reader["id"],
        "due_date": (date.today() + timedelta(days=7)).isoformat(),
    }
    assert client.post("/loans", json=payload).status_code == 201
    assert client.post("/loans", json=payload).status_code == 409
