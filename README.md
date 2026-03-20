# Czyszczenie

> Aplikacja desktopowa do szybkiego przeglądania i usuwania zdjęć oraz PDF-ów.

Zamiast klikać w menedżerze plików, przeglądasz pliki jeden po jednym i decydujesz jednym klawiszem — zostaw lub usuń. Działa na Linuksie, macOS i Windows.

## Spis treści

- [Funkcje](#funkcje)
- [Wymagania](#wymagania)
- [Instalacja](#instalacja)
- [Uruchomienie](#uruchomienie)
- [Sterowanie](#sterowanie)
- [Obsługiwane formaty](#obsługiwane-formaty)

## Funkcje

- Przeglądanie zdjęć i PDF-ów plik po pliku, posortowanych od najnowszych
- Usuwanie z możliwością cofnięcia ostatniej decyzji
- Obsługa wielostronicowych PDF-ów
- Automatyczne skalowanie obrazu do rozmiaru okna
- Sterowanie klawiaturą (WASD + klawiatura numeryczna)
- Opcjonalne skanowanie wybranego katalogu zamiast domowego

## Wymagania

- Python 3.8+
- [Pillow](https://python-pillow.org/)
- [PyMuPDF](https://pymupdf.readthedocs.io/)

## Instalacja

```bash
pip install pillow pymupdf
```

## Uruchomienie

```bash
# Skanuje katalog domowy (~)
python3 czyszczenie.py

# Skanuje wybrany katalog
python3 czyszczenie.py /ścieżka/do/katalogu
```

Po uruchomieniu pojawia się okno wyboru trybu — **Obrazy** lub **PDF-y**.

## Sterowanie

| Klawisz   | Akcja                                         |
|-----------|-----------------------------------------------|
| `A` / `4` | Zostaw plik, przejdź dalej                    |
| `D` / `6` | Usuń plik, przejdź dalej                      |
| `Q` / `7` | Cofnij ostatnie usunięcie                     |
| `W` / `8` | Poprzednia strona PDF *(tylko tryb PDF)*      |
| `S` / `5` | Następna strona PDF *(tylko tryb PDF)*        |
| `Esc`     | Zamknij aplikację                             |

## Obsługiwane formaty

**Obrazy:** `.jpg` `.jpeg` `.png` `.gif` `.bmp` `.webp` `.tiff` `.avif` `.heic` `.heif` `.ico` `.tga` `.ppm`

**Dokumenty:** `.pdf`
