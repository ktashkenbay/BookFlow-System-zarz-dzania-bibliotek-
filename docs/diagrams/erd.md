# Diagram ERD

```mermaid
erDiagram
    BOOKS ||--o{ LOANS : "jest przedmiotem"
    READERS ||--o{ LOANS : "posiada historie"

    BOOKS {
        int id PK
        string title
        string author
        string isbn UK "opcjonalny"
        int copies
    }
    READERS {
        int id PK
        string full_name
        string email UK
    }
    LOANS {
        int id PK
        int book_id FK
        int reader_id FK
        date borrowed_at
        date due_date
        date returned_at "NULL oznacza aktywne"
    }
```

### Ograniczenia

- `books.isbn` jest unikalny, ale może być pusty (`NULL`).
- `readers.email` jest wymagany i unikalny.
- `loans.book_id` wskazuje na `books.id`, a `loans.reader_id` na `readers.id`.
- Aktywne wypożyczenie identyfikuje `returned_at IS NULL`.
- Liczba aktywnych rekordów `loans` dla książki nie może przekraczać `books.copies` (reguła egzekwowana przez API).
