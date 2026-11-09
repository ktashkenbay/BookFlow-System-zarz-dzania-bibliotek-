# BookFlow – System zarządzania biblioteką

BookFlow to prosty system dla bibliotekarzy, który pozwala katalogować książki, rejestrować czytelników oraz obsługiwać wypożyczenia i zwroty.

## Cel projektu

Projekt dostarcza małe REST API do podstawowej obsługi biblioteki. Dokumentacja i implementacja opisują ten sam zakres: książki, czytelników oraz wypożyczenia z kontrolą dostępności egzemplarzy.

## Funkcje MVP

- dodawanie i przeglądanie książek,
- dodawanie i przeglądanie czytelników,
- rejestrowanie wypożyczenia z kontrolą liczby dostępnych egzemplarzy,
- zwracanie wypożyczonej książki,
- przeglądanie aktywnych wypożyczeń,
- trwały zapis danych w SQLite.

## Technologie

- Python 3.10+
- FastAPI
- SQLAlchemy 2
- SQLite
- pytest i HTTPX

## Uruchomienie lokalne

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Interaktywna dokumentacja API: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs). Domyślna baza `bookflow.db` powstaje w katalogu projektu. Ścieżkę można zmienić zmienną `BOOKFLOW_DATABASE_URL`.

## Testy

```bash
pytest
```

## API

| Metoda | Endpoint | Opis |
|---|---|---|
| `POST` | `/books` | Dodaje książkę |
| `GET` | `/books` | Zwraca katalog wraz z dostępnością |
| `POST` | `/readers` | Rejestruje czytelnika |
| `GET` | `/readers` | Zwraca listę czytelników |
| `POST` | `/loans` | Wypożycza egzemplarz |
| `GET` | `/loans/active` | Zwraca aktywne wypożyczenia |
| `POST` | `/loans/{loan_id}/return` | Rejestruje zwrot |

Szczegóły wymagań, przypadki użycia i diagramy znajdują się w [`docs/README.md`](docs/README.md) oraz [`docs/diagrams/`](docs/diagrams/).

## Zakres i ograniczenia

To edukacyjna wersja MVP. Nie obejmuje logowania, ról, opłat za przetrzymanie, rezerwacji, powiadomień ani interfejsu webowego. Przed wdrożeniem produkcyjnym należy dodać uwierzytelnianie, migracje bazy, kopie zapasowe i dodatkowe zabezpieczenia.
