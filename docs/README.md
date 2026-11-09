## Dokumentacja projektu

### Opis i cel

**BookFlow – System zarządzania biblioteką** to REST API dla bibliotekarza, który potrzebuje prowadzić katalog książek, ewidencję czytelników oraz rejestrować wypożyczenia i zwroty. System przechowuje dane w relacyjnej bazie SQLite.

### Użytkownicy i zakres

- **Bibliotekarz** – korzysta z endpointów API, aby zarządzać katalogiem, czytelnikami i obiegiem książek.
- **Czytelnik** – jest osobą zapisaną w systemie; w MVP nie loguje się samodzielnie.

Zakres MVP obejmuje książki, czytelników, wypożyczenia i zwroty. Zasada dostępności: liczba aktywnych wypożyczeń książki nie może przekraczać liczby jej egzemplarzy. Wypożyczenie ma termin zwrotu późniejszy niż bieżąca data.

### Wymagania funkcjonalne

1. System umożliwia dodanie i przeglądanie książek (tytuł, autor, opcjonalny ISBN, liczba egzemplarzy).
2. System umożliwia dodanie i przeglądanie czytelników (imię i nazwisko, unikalny adres e-mail).
3. System umożliwia wypożyczenie istniejącej książki istniejącemu czytelnikowi, jeżeli jest dostępny egzemplarz.
4. System zapisuje datę wypożyczenia i termin zwrotu.
5. System umożliwia zwrot aktywnego wypożyczenia i zapisuje datę zwrotu.
6. System udostępnia listę aktywnych wypożyczeń oraz aktualną dostępność książek.

### Wymagania niefunkcjonalne

- HTTP API jest opisane automatycznie przez OpenAPI/FastAPI.
- Walidacja wejścia zwraca błędy 422; brak zasobu zwraca 404; konflikt (duplikat lub brak egzemplarza) zwraca 409.
- Dane są trwale przechowywane w SQLite.
- Projekt wymaga Python 3.10 lub nowszego.

### Przypadki użycia

| ID | Aktor | Przypadek użycia | Warunki / rezultat |
|---|---|---|---|
| UC-01 | Bibliotekarz | Dodaje książkę | Książka z poprawnymi danymi zostaje dodana do katalogu. |
| UC-02 | Bibliotekarz | Przegląda katalog | Otrzymuje listę książek z liczbą dostępnych egzemplarzy. |
| UC-03 | Bibliotekarz | Rejestruje czytelnika | Czytelnik zostaje zapisany; e-mail musi być unikalny. |
| UC-04 | Bibliotekarz | Wypożycza książkę | Przy istniejącym czytelniku i dostępnej książce powstaje aktywne wypożyczenie. |
| UC-05 | Bibliotekarz | Rejestruje zwrot | Aktywne wypożyczenie zostaje zamknięte datą zwrotu. |
| UC-06 | Bibliotekarz | Sprawdza aktywne wypożyczenia | Otrzymuje listę niezwróconych książek wraz z terminami. |

### Interfejs API

Szczegółowe schematy request/response są dostępne w `/docs` po uruchomieniu aplikacji.

| Endpoint | Znaczenie | Typowe odpowiedzi |
|---|---|---|
| `POST /books` | Dodanie książki | 201, 409 |
| `GET /books` | Katalog z dostępnością | 200 |
| `POST /readers` | Rejestracja czytelnika | 201, 409, 422 |
| `GET /readers` | Lista czytelników | 200 |
| `POST /loans` | Wypożyczenie | 201, 404, 409, 422 |
| `GET /loans/active` | Aktywne wypożyczenia | 200 |
| `POST /loans/{loan_id}/return` | Zwrot wypożyczenia | 200, 404, 409 |
| `GET /health` | Kontrola działania | 200 |

Przykład wypożyczenia: `{"book_id": 1, "reader_id": 1, "due_date": "2030-01-30"}`.

### Reguły domenowe i walidacja

- Książka musi mieć tytuł, autora i co najmniej jeden egzemplarz.
- ISBN, jeśli podany, jest unikalny.
- E-mail czytelnika jest unikalny i walidowany jako adres e-mail.
- Wypożyczyć można wyłącznie istniejącą książkę i istniejącego czytelnika.
- Nie można wypożyczyć, gdy brak dostępnych egzemplarzy.
- Termin zwrotu musi być późniejszy niż dzisiejsza data.
- Zwrot można zarejestrować tylko raz dla danego wypożyczenia.

### Model danych

Relacyjny model danych przedstawiono na diagramie ERD. `Loan` jest rekordem historii wypożyczenia; `returned_at = NULL` oznacza wypożyczenie aktywne. Szczegóły: [`diagrams/erd.md`](diagrams/erd.md).

### Założenia i przyszły rozwój

System zakłada, że administrator biblioteki jest zaufanym użytkownikiem API. MVP nie ma uwierzytelniania, autoryzacji, blokad współbieżności dla wielu równoległych stanowisk, migracji schematu ani interfejsu graficznego. Dalszy rozwój może dodać role i logowanie, rezerwacje, powiadomienia, kary, migracje Alembic oraz aplikację webową.

### Uruchomienie i testowanie

Instrukcje znajdują się w głównym [README](../README.md). Testy automatyczne uruchamia się poleceniem `pytest`.
