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
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".m4v"}
VIDEO_MAX_SECONDS = 600  # 10 minut


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
    """Okno wyboru trybu: obrazy, PDF-y lub filmy. Zwraca 'images', 'pdfs' lub 'videos'."""
    result = {"mode": None}

    win = tk.Tk()
    win.title("Czyszczenie — wybór trybu")
    win.configure(bg="#111")
    win.resizable(False, False)

    w, h = 500, 160
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

    vid_frame = tk.Frame(btn_frame, bg="#111")
    vid_frame.pack(side="left", padx=12, pady=10)
    tk.Button(
        vid_frame,
        text="🎬  Filmy",
        font=("monospace", 12),
        width=12,
        bg="#a62",
        fg="white",
        activebackground="#b73",
        cursor="hand2",
        command=lambda: choose("videos"),
    ).pack()
    tk.Label(
        vid_frame, text="[ 2 / V ]", bg="#111", fg="#888", font=("monospace", 9)
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
    win.bind("<v>", lambda e: choose("videos"))
    win.bind("<V>", lambda e: choose("videos"))
    win.bind("<2>", lambda e: choose("videos"))
    win.bind("<KP_2>", lambda e: choose("videos"))
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

        titles = {"pdfs": "Czyszczenie PDF-ów", "videos": "Czyszczenie filmów"}
        root.title(titles.get(mode, "Czyszczenie zdjęć"))
        root.configure(bg="#111")
        root.geometry("1000x750")
        root.resizable(True, True)
        root.protocol("WM_DELETE_WINDOW", self.quit)

        self.info_label = tk.Label(
            root, bg="#222", fg="white", font=("monospace", 13), pady=10
        )
        self.info_label.pack(fill="x", side="bottom")

        self.filename_label = tk.Label(
            root, bg="#111", fg="#aaa", font=("monospace", 10)
        )
        self.filename_label.pack(side="bottom", pady=(0, 4))

        self.image_label = tk.Label(root, bg="#111", cursor="none")
        self.image_label.pack(expand=True, fill="both", padx=10, pady=(10, 0))

        root.bind("<a>", lambda e: self.on_key_keep())
        root.bind("<A>", lambda e: self.on_key_keep())
        root.bind("<4>", lambda e: self.on_key_keep())
        root.bind("<KP_4>", lambda e: self.on_key_keep())
        root.bind("<d>", lambda e: self.on_key_delete())
        root.bind("<D>", lambda e: self.on_key_delete())
        root.bind("<6>", lambda e: self.on_key_delete())
        root.bind("<KP_6>", lambda e: self.on_key_delete())
        root.bind("<q>", lambda e: self.on_key_restore())
        root.bind("<Q>", lambda e: self.on_key_restore())
        root.bind("<7>", lambda e: self.on_key_restore())
        root.bind("<KP_7>", lambda e: self.on_key_restore())
        root.bind("<Escape>", lambda e: self.quit())
        root.bind("<Configure>", lambda e: self.on_resize())

        self._current_path = None
        self._last_size = (0, 0)
        self.pdf_page = 0
        self.pdf_page_count = 1
        self._video_cap = None
        self._video_fps = 30
        self._video_frame_limit = 0
        self._video_after_id = None

        if mode == "pdfs":
            root.bind("<8>", lambda e: self.pdf_prev_page())
            root.bind("<KP_8>", lambda e: self.pdf_prev_page())
            root.bind("<w>", lambda e: self.pdf_prev_page())
            root.bind("<W>", lambda e: self.pdf_prev_page())
            root.bind("<5>", lambda e: self.pdf_next_page())
            root.bind("<KP_5>", lambda e: self.pdf_next_page())
            root.bind("<s>", lambda e: self.pdf_next_page())
            root.bind("<S>", lambda e: self.pdf_next_page())
        elif mode == "videos":
            root.bind("<8>", lambda e: self.video_seek(30))
            root.bind("<KP_8>", lambda e: self.video_seek(30))
            root.bind("<w>", lambda e: self.video_seek(30))
            root.bind("<W>", lambda e: self.video_seek(30))
            root.bind("<5>", lambda e: self.video_seek(-30))
            root.bind("<KP_5>", lambda e: self.video_seek(-30))
            root.bind("<s>", lambda e: self.video_seek(-30))
            root.bind("<S>", lambda e: self.video_seek(-30))

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

    # --- wideo ---

    def _stop_video(self):
        if self._video_after_id is not None:
            self.root.after_cancel(self._video_after_id)
            self._video_after_id = None
        if self._video_cap is not None:
            self._video_cap.release()
            self._video_cap = None

    def _start_video(self, path):
        import cv2

        self._stop_video()
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            raise IOError(f"Nie można otworzyć: {path}")
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        self._video_cap = cap
        self._video_fps = fps
        self._video_frame_limit = int(min(total_frames, fps * VIDEO_MAX_SECONDS))
        self._play_video_frame()

    def _play_video_frame(self):
        import cv2

        if self._video_cap is None or self.finished:
            return
        pos = self._video_cap.get(cv2.CAP_PROP_POS_FRAMES)
        if self._video_frame_limit > 0 and pos >= self._video_frame_limit:
            self._video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = self._video_cap.read()
        if not ret:
            self._video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self._video_after_id = self.root.after(100, self._play_video_frame)
            return
        w = max(self.image_label.winfo_width(), 800)
        h = max(self.image_label.winfo_height(), 550)
        fh, fw = frame.shape[:2]
        scale = min(w / fw, h / fh)
        frame = cv2.resize(
            frame, (int(fw * scale), int(fh * scale)), interpolation=cv2.INTER_LINEAR
        )
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self._photo = ImageTk.PhotoImage(Image.fromarray(frame))
        self.image_label.configure(image=self._photo, text="")
        delay = max(1, int(1000 / self._video_fps))
        self._video_after_id = self.root.after(delay, self._play_video_frame)

    def video_seek(self, seconds):
        import cv2

        if self._video_cap is None or self.finished:
            return
        current_ms = self._video_cap.get(cv2.CAP_PROP_POS_MSEC)
        new_ms = max(0, current_ms + seconds * 1000)
        if self._video_frame_limit > 0:
            limit_ms = (self._video_frame_limit / self._video_fps) * 1000
            new_ms = min(new_ms, limit_ms)
        if seconds < 0:
            path = self._current_path
            self._video_cap.release()
            self._video_cap = cv2.VideoCapture(path)
        self._video_cap.set(cv2.CAP_PROP_POS_MSEC, new_ms)

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
        self._stop_video()
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
        if self.mode == "videos":
            return
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

        historia_info = "  [Q / 7] Cofnij usunięcie" if self.history else ""

        self._stop_video()
        try:
            if self.mode == "videos":
                self._start_video(path)
            else:
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
            scroll_info = f"   [S / 5] Następna str.   [W / 8] Poprzednia str.   ({self.pdf_page + 1}/{self.pdf_page_count})"
        elif self.mode == "videos":
            scroll_info = (
                f"   [W / 8] -30s   [S / 5] +30s   (max {VIDEO_MAX_SECONDS // 60} min)"
            )
        else:
            scroll_info = ""
        self.info_label.configure(
            text=f"[{self.index + 1} / {total}]   "
            f"[A / 4] Zostaw   [D / 6] Usuń"
            f"{scroll_info}"
            f"{historia_info}   |   "
            f"Zostawiono: {self.kept}   Usunięto: {self.deleted}"
        )

    def _update_pdf_info(self):
        if self.finished or not self._current_path:
            return
        total = len(self.images)
        historia_info = "  [Q / 7] Cofnij usunięcie" if self.history else ""
        filename = os.path.relpath(self._current_path, PICTURES_DIR)
        date_str = datetime.fromtimestamp(
            os.path.getmtime(self._current_path)
        ).strftime("%d.%m.%Y  %H:%M")
        self.filename_label.configure(text=f"{filename}   •   {date_str}")
        self.info_label.configure(
            text=f"[{self.index + 1} / {total}]   "
            f"[A / 4] Zostaw   [D / 6] Usuń"
            f"   [S / 5] Następna str.   [W / 8] Poprzednia str.   ({self.pdf_page + 1}/{self.pdf_page_count})"
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
        self._stop_video()
        self.finished = True
        self._current_path = None
        historia_info = "   [Q / 7] Cofnij ostatnie usunięcie" if self.history else ""
        self._photo = None
        self.image_label.configure(
            image="", text="Gotowe!", fg="white", font=("monospace", 42)
        )
        self.filename_label.configure(text="")
        self.info_label.configure(
            text=f"Zostawiono: {self.kept}   Usunięto: {self.deleted}"
            f"{historia_info}   |   "
            f"[A / 4 / D / 6] Zakończ   [ESC] Zakończ"
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
    elif mode == "videos":
        extensions = VIDEO_EXTENSIONS
        label = "filmów"
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
