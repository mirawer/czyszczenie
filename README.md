# Czyszczenie

> Aplikacja desktopowa do szybkiego przeglądania i usuwania zdjęć, PDF-ów oraz filmów.

Zamiast klikać w menedżerze plików, przeglądasz pliki jeden po jednym i decydujesz jednym klawiszem — zostaw lub usuń. Działa na Linuksie, macOS i Windows.

## Spis treści

- [Funkcje](#funkcje)
- [Wymagania](#wymagania)
- [Instalacja](#instalacja)
- [Uruchomienie](#uruchomienie)
- [Sterowanie](#sterowanie)
- [Obsługiwane formaty](#obsługiwane-formaty)

## Funkcje

- Przeglądanie zdjęć, PDF-ów i filmów plik po pliku, posortowanych od najnowszych
- Usuwanie z możliwością cofnięcia ostatniej decyzji
- Obsługa wielostronicowych PDF-ów
- Odtwarzanie filmów z przewijaniem ±30s (limit 10 minut)
- Automatyczne skalowanie do rozmiaru okna
- Sterowanie klawiaturą (WASD + klawiatura numeryczna)
- Opcjonalne skanowanie wybranego katalogu zamiast domowego

## Wymagania

- Python 3.8+
- [Pillow](https://python-pillow.org/)
- [PyMuPDF](https://pymupdf.readthedocs.io/)
- [opencv-python](https://pypi.org/project/opencv-python/) — tylko tryb filmów

## Instalacja

```bash
pip install pillow pymupdf opencv-python
```

## Uruchomienie

```bash
# Skanuje katalog domowy (~)
python3 czyszczenie.py

# Skanuje wybrany katalog
python3 czyszczenie.py /ścieżka/do/katalogu
```

Po uruchomieniu pojawia się okno wyboru trybu — **Obrazy**, **PDF-y** lub **Filmy**.

## Sterowanie

### Wszystkie tryby

| Klawisz   | Akcja                     |
|-----------|---------------------------|
| `A` / `4` | Zostaw plik, przejdź dalej |
| `D` / `6` | Usuń plik, przejdź dalej  |
| `Q` / `7` | Cofnij ostatnie usunięcie |
| `Esc`     | Zamknij aplikację         |

### Tryb PDF

| Klawisz   | Akcja              |
|-----------|--------------------|
| `W` / `8` | Poprzednia strona  |
| `S` / `5` | Następna strona    |

### Tryb filmów

| Klawisz   | Akcja          |
|-----------|----------------|
| `W` / `8` | Cofnij 30s     |
| `S` / `5` | Przewiń 30s    |

## Obsługiwane formaty

**Obrazy:** `.jpg` `.jpeg` `.png` `.gif` `.bmp` `.webp` `.tiff` `.avif` `.heic` `.heif` `.ico` `.tga` `.ppm`

**Dokumenty:** `.pdf`

**Filmy:** `.mp4` `.avi` `.mov` `.mkv` `.webm` `.m4v`
