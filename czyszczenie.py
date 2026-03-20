#!/usr/bin/env python3
import os
import sys
import tkinter as tk
from datetime import datetime

from PIL import Image, ImageTk

PICTURES_DIR = os.path.expanduser("~")
IMG_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".jpe",
    ".jfif",
    ".png",
    ".gif",
    ".bmp",
    ".webp",
    ".tiff",
    ".tif",
    ".avif",
    ".heic",
    ".heif",
    ".ico",
    ".tga",
    ".ppm",
}
PDF_EXTENSIONS = {".pdf"}


def get_files(extensions):
    files = []
    for root, _, filenames in os.walk(PICTURES_DIR):
        for f in filenames:
            if os.path.splitext(f.lower())[1] in extensions:
                full = os.path.join(root, f)
                files.append((os.path.getmtime(full), full))
    files.sort(reverse=True)
    return [f[1] for f in files]


def load_pdf_as_image(path, max_w, max_h, page_num=0):
    import fitz

    doc = fitz.open(path)
    page_num = max(0, min(page_num, len(doc) - 1))
    page = doc[page_num]
    zoom = min(max_w / page.rect.width, max_h / page.rect.height, 2.0)
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    page_count = len(doc)
    doc.close()
    return img, page_count


def ask_mode():
    """Okno wyboru trybu: obrazy lub PDF-y. Zwraca 'images' lub 'pdfs'."""
    result = {"mode": None}

    win = tk.Tk()
    win.title("Czyszczenie — wybór trybu")
    win.configure(bg="#111")
    win.resizable(False, False)

    w, h = 340, 160
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    win.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    tk.Label(
        win,
        text="Co chcesz przeglądać?",
        bg="#111",
        fg="white",
        font=("monospace", 14),
        pady=20,
    ).pack()

    btn_frame = tk.Frame(win, bg="#111")
    btn_frame.pack()

    def choose(mode):
        result["mode"] = mode
        win.destroy()

    img_frame = tk.Frame(btn_frame, bg="#111")
    img_frame.pack(side="left", padx=12, pady=10)
    tk.Button(
        img_frame,
        text="🖼  Obrazy",
        font=("monospace", 12),
        width=12,
        bg="#2a6",
        fg="white",
        activebackground="#3b7",
        cursor="hand2",
        command=lambda: choose("images"),
    ).pack()
    tk.Label(
        img_frame, text="[ 1 / Z ]", bg="#111", fg="#888", font=("monospace", 9)
    ).pack()

    pdf_frame = tk.Frame(btn_frame, bg="#111")
    pdf_frame.pack(side="left", padx=12, pady=10)
    tk.Button(
        pdf_frame,
        text="📄  PDF-y",
        font=("monospace", 12),
        width=12,
        bg="#26a",
        fg="white",
        activebackground="#37b",
        cursor="hand2",
        command=lambda: choose("pdfs"),
    ).pack()
    tk.Label(
        pdf_frame, text="[ 3 / U ]", bg="#111", fg="#888", font=("monospace", 9)
    ).pack()

    win.bind("<Escape>", lambda e: win.destroy())
    win.bind("<z>", lambda e: choose("images"))
    win.bind("<Z>", lambda e: choose("images"))
    win.bind("<1>", lambda e: choose("images"))
    win.bind("<KP_1>", lambda e: choose("images"))
    win.bind("<u>", lambda e: choose("pdfs"))
    win.bind("<U>", lambda e: choose("pdfs"))
    win.bind("<3>", lambda e: choose("pdfs"))
    win.bind("<KP_3>", lambda e: choose("pdfs"))
    win.mainloop()
    return result["mode"]


class App:
    def __init__(self, root, images, mode="images"):
        self.root = root
        self.images = images
        self.mode = mode  # 'images' lub 'pdfs'
        self.index = 0
        self.deleted = 0
        self.kept = 0
        self.history = None  # ścieżka ostatnio "usuniętego" pliku (jeszcze na dysku)
        self.finished = False
        self._photo = None

        root.title("Czyszczenie PDF-ów" if mode == "pdfs" else "Czyszczenie zdjęć")
        root.configure(bg="#111")
        root.geometry("1000x750")
        root.resizable(True, True)
        root.protocol("WM_DELETE_WINDOW", self.quit)

        self.image_label = tk.Label(root, bg="#111", cursor="none")
        self.image_label.pack(expand=True, fill="both", padx=10, pady=(10, 0))

        self.filename_label = tk.Label(
            root, bg="#111", fg="#aaa", font=("monospace", 10)
        )
        self.filename_label.pack(pady=(4, 0))

        self.info_label = tk.Label(
            root, bg="#222", fg="white", font=("monospace", 13), pady=10
        )
        self.info_label.pack(fill="x", side="bottom")

        root.bind("<z>", lambda e: self.on_key_keep())
        root.bind("<Z>", lambda e: self.on_key_keep())
        root.bind("<1>", lambda e: self.on_key_keep())
        root.bind("<KP_1>", lambda e: self.on_key_keep())
        root.bind("<u>", lambda e: self.on_key_delete())
        root.bind("<U>", lambda e: self.on_key_delete())
        root.bind("<3>", lambda e: self.on_key_delete())
        root.bind("<KP_3>", lambda e: self.on_key_delete())
        root.bind("<p>", lambda e: self.on_key_restore())
        root.bind("<P>", lambda e: self.on_key_restore())
        root.bind("<Escape>", lambda e: self.quit())
        root.bind("<Configure>", lambda e: self.on_resize())

        self._current_path = None
        self._last_size = (0, 0)
        self.pdf_page = 0
        self.pdf_page_count = 1

        if mode == "pdfs":
            root.bind("<8>", lambda e: self.pdf_prev_page())
            root.bind("<KP_8>", lambda e: self.pdf_prev_page())
            root.bind("<2>", lambda e: self.pdf_next_page())
            root.bind("<KP_2>", lambda e: self.pdf_next_page())
        else:
            root.bind("<8>", lambda e: self.on_key_restore())
            root.bind("<KP_8>", lambda e: self.on_key_restore())

        self.show_current()

    # --- obsługa klawiszy ---

    def on_key_keep(self):
        if self.finished:
            self.quit()
        else:
            self.keep()

    def on_key_delete(self):
        if self.finished:
            self.quit()
        else:
            self.delete()

    def on_key_restore(self):
        self.restore_and_review()

    def pdf_next_page(self):
        if self.finished or self.pdf_page >= self.pdf_page_count - 1:
            return
        self.pdf_page += 1
        self._refresh_image()

    def pdf_prev_page(self):
        if self.finished or self.pdf_page <= 0:
            return
        self.pdf_page -= 1
        self._refresh_image()

    # --- logika ---

    def keep(self):
        self.kept += 1
        self.index += 1
        self.show_current()

    def delete(self):
        path = self.images[self.index]
        # jeśli w historii jest poprzednie zdjęcie — teraz je trwale kasujemy
        if self.history is not None:
            try:
                os.remove(self.history)
            except Exception as e:
                print(f"Błąd usuwania z historii {self.history}: {e}")
        # nowe zdjęcie trafia do historii (nie kasujemy go jeszcze)
        self.history = path
        self.deleted += 1
        self.index += 1
        self.show_current()

    def restore_and_review(self):
        if self.history is None:
            return
        # cofamy: wracamy do zdjęcia z historii
        restored = self.history
        self.history = None
        self.deleted -= 1
        # wstawiamy je z powrotem na aktualną pozycję
        self.index -= 1
        self.images[self.index] = restored
        self.finished = False
        self.show_current()

    def quit(self):
        # usuń co zostało w historii
        if self.history is not None:
            try:
                os.remove(self.history)
            except Exception as e:
                print(f"Błąd usuwania historii {self.history}: {e}")
        self.root.destroy()

    # --- wyświetlanie ---

    def load_image(self, path):
        w = max(self.image_label.winfo_width(), 800)
        h = max(self.image_label.winfo_height(), 550)
        if self.mode == "pdfs":
            img, count = load_pdf_as_image(path, w, h, self.pdf_page)
            self.pdf_page_count = count
        else:
            img = Image.open(path)
            img.thumbnail((w, h), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)

    def _refresh_image(self):
        if not self._current_path or not os.path.exists(self._current_path):
            return
        try:
            photo = self.load_image(self._current_path)
            self._photo = photo
            self.image_label.configure(image=self._photo)
        except Exception:
            pass
        if self.mode == "pdfs":
            self._update_pdf_info()

    def show_current(self):
        if self.index >= len(self.images):
            self.finish()
            return

        self.finished = False
        self.pdf_page = 0
        path = self.images[self.index]
        self._current_path = path
        filename = os.path.relpath(path, PICTURES_DIR)
        date_str = datetime.fromtimestamp(os.path.getmtime(path)).strftime(
            "%d.%m.%Y  %H:%M"
        )
        total = len(self.images)

        if self.mode == "pdfs":
            historia_info = "  [P] Cofnij usunięcie" if self.history else ""
        else:
            historia_info = "  [P / 8] Cofnij usunięcie" if self.history else ""

        try:
            photo = self.load_image(path)
            self._photo = photo
            self.image_label.configure(image=self._photo, text="")
        except Exception:
            self._photo = None
            self.image_label.configure(
                image="",
                text="[ Nie można otworzyć pliku ]",
                fg="#f66",
                font=("monospace", 14),
            )

        self.filename_label.configure(text=f"{filename}   •   {date_str}")
        if self.mode == "pdfs":
            scroll_info = f"   [2] Następna str.   [8] Poprzednia str.   ({self.pdf_page + 1}/{self.pdf_page_count})"
        else:
            scroll_info = ""
        self.info_label.configure(
            text=f"[{self.index + 1} / {total}]   "
            f"[Z / 1] Zostaw   [U / 3] Usuń"
            f"{scroll_info}"
            f"{historia_info}   |   "
            f"Zostawiono: {self.kept}   Usunięto: {self.deleted}"
        )

    def _update_pdf_info(self):
        if self.finished or not self._current_path:
            return
        total = len(self.images)
        historia_info = "  [P] Cofnij usunięcie" if self.history else ""
        filename = os.path.relpath(self._current_path, PICTURES_DIR)
        date_str = datetime.fromtimestamp(
            os.path.getmtime(self._current_path)
        ).strftime("%d.%m.%Y  %H:%M")
        self.filename_label.configure(text=f"{filename}   •   {date_str}")
        self.info_label.configure(
            text=f"[{self.index + 1} / {total}]   "
            f"[Z / 1] Zostaw   [U / 3] Usuń"
            f"   [2] Następna str.   [8] Poprzednia str.   ({self.pdf_page + 1}/{self.pdf_page_count})"
            f"{historia_info}   |   "
            f"Zostawiono: {self.kept}   Usunięto: {self.deleted}"
        )

    def on_resize(self):
        size = (self.root.winfo_width(), self.root.winfo_height())
        if size == self._last_size:
            return
        self._last_size = size
        self._refresh_image()

    def finish(self):
        self.finished = True
        self._current_path = None
        historia_info = "   [P / 8] Cofnij ostatnie usunięcie" if self.history else ""
        self._photo = None
        self.image_label.configure(
            image="", text="Gotowe!", fg="white", font=("monospace", 42)
        )
        self.filename_label.configure(text="")
        self.info_label.configure(
            text=f"Zostawiono: {self.kept}   Usunięto: {self.deleted}"
            f"{historia_info}   |   "
            f"[Z / 1 / U / 3] Zakończ   [ESC] Zakończ"
        )


def main():
    global PICTURES_DIR

    if len(sys.argv) > 1:
        target = os.path.abspath(sys.argv[1])
        if not os.path.isdir(target):
            print(f'Błąd: "{target}" nie jest katalogiem.')
            sys.exit(1)
        PICTURES_DIR = target

    mode = ask_mode()
    if mode is None:
        sys.exit(0)

    if mode == "pdfs":
        extensions = PDF_EXTENSIONS
        label = "PDF-ów"
    else:
        extensions = IMG_EXTENSIONS
        label = "zdjęć"

    files = get_files(extensions)
    if not files:
        print(f"Brak {label} w katalogu: {PICTURES_DIR}")
        sys.exit(1)

    print(f"Znaleziono {len(files)} {label} w: {PICTURES_DIR}")
    root = tk.Tk()
    App(root, files, mode=mode)
    root.mainloop()


if __name__ == "__main__":
    main()
