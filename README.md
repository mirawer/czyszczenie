# Czyszczenie

Prosta aplikacja desktopowa do przeglądania i usuwania zdjęć oraz PDF-ów. Pozwala szybko przejrzeć pliki jeden po drugim i zdecydować, co zostawić, a co usunąć — bez klikania w menedżerze plików.

## Funkcje

- Przeglądanie zdjęć i PDF-ów plik po pliku
- Usuwanie pliku z możliwością cofnięcia (jedno cofnięcie wstecz)
- Obsługa wielu stron w PDF-ach
- Skalowanie obrazu do okna
- Sterowanie klawiaturą i myszą
- Obsługa podkatalogu jako argumentu startowego

## Wymagania

```
pip install pillow pymupdf
```

- Python 3.8+
- [Pillow](https://python-pillow.org/) — obsługa obrazów
- [PyMuPDF](https://pymupdf.readthedocs.io/) (`fitz`) — obsługa PDF-ów

## Uruchomienie

```bash
# Skanuje katalog domowy (~)
python3 czyszczenie.py

# Skanuje podany katalog
python3 czyszczenie.py /ścieżka/do/katalogu
```

Po uruchomieniu pojawia się okno wyboru trybu — **Obrazy** lub **PDF-y**.

## Sterowanie

| Klawisz | Akcja |
|---------|-------|
| `Z` / `1` | Zostaw plik, przejdź dalej |
| `U` / `3` | Usuń plik, przejdź dalej |
| `P` / `8` | Cofnij ostatnie usunięcie |
| `2` | Następna strona PDF |
| `8` | Poprzednia strona PDF (tylko tryb PDF) |
| `Esc` | Zamknij aplikację |

> Uwaga: klawisz `8` cofa usunięcie w trybie obrazów, a przewija strony w trybie PDF.

## Obsługiwane formaty

**Obrazy:** `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`, `.tiff`, `.avif`, `.heic`, `.heif`, `.ico`, `.tga`, `.ppm`

**Dokumenty:** `.pdf`
