"""
Bulk File Renamer
Author: CODEX-M41NUL
Run on: Pydroid 3 (Python 3, Tkinter)

Features:
- Pick a folder, list all files
- Rename modes: Add Prefix, Add Suffix, Find & Replace, Sequential Numbering,
  Change Extension, Lowercase/Uppercase
- Live preview before applying
- Undo last rename batch
- Colorful dark / gradient-accent UI
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------
BG_DARK = "#0f0f1a"
BG_PANEL = "#181826"
BG_CARD = "#1f1f33"
ACCENT_1 = "#ff6a00"   # orange
ACCENT_2 = "#ffb347"   # amber
ACCENT_PURPLE = "#8a5cff"
ACCENT_PINK = "#ff4fa3"
ACCENT_CYAN = "#3ee6d8"
TEXT_MAIN = "#f2f2f7"
TEXT_DIM = "#9a9ab0"
SUCCESS = "#3ee67e"
DANGER = "#ff4f6d"

FONT_TITLE = ("Helvetica", 20, "bold")
FONT_SUB = ("Helvetica", 10)
FONT_LABEL = ("Helvetica", 11, "bold")
FONT_NORMAL = ("Helvetica", 10)
FONT_BTN = ("Helvetica", 11, "bold")


class GradientButton(tk.Canvas):
    """A flat 'glass' button with a colored border glow, since Tk has no real gradients."""

    def __init__(self, parent, text, command, color=ACCENT_1, width=160, height=42, **kw):
        super().__init__(parent, width=width, height=height, bg=BG_PANEL,
                          highlightthickness=0, **kw)
        self.command = command
        self.color = color
        self.text = text
        self.width = width
        self.height = height
        self._draw("normal")
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", lambda e: self._draw("hover"))
        self.bind("<Leave>", lambda e: self._draw("normal"))

    def _draw(self, state):
        self.delete("all")
        fill = BG_CARD if state == "normal" else self.color
        text_color = TEXT_MAIN
        r = 12
        self._round_rect(2, 2, self.width - 2, self.height - 2, r,
                          fill=fill, outline=self.color, width=2)
        self.create_text(self.width / 2, self.height / 2, text=self.text,
                          fill=text_color, font=FONT_BTN)

    def _round_rect(self, x1, y1, x2, y2, r, **kw):
        points = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r, x2, y2,
                  x2-r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y1+r, x1, y1]
        self.create_polygon(points, smooth=True, **kw)

    def _on_click(self, e):
        if self.command:
            self.command()


class RoundedFrame(tk.Canvas):
    """A card-like rounded rectangle container used as a background panel."""

    def __init__(self, parent, color=BG_CARD, radius=18, **kw):
        super().__init__(parent, bg=BG_DARK, highlightthickness=0, **kw)
        self.color = color
        self.radius = radius
        self.bind("<Configure>", self._redraw)

    def _redraw(self, event=None):
        self.delete("bg")
        w = self.winfo_width()
        h = self.winfo_height()
        r = self.radius
        if w < 2 or h < 2:
            return
        points = [r, 0, w-r, 0, w, 0, w, r, w, h-r, w, h,
                  w-r, h, r, h, 0, h, 0, h-r, 0, r, 0, 0]
        self.create_polygon(points, smooth=True, fill=self.color, tags="bg")
        self.tag_lower("bg")


class BulkRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bulk File Renamer")
        self.root.geometry("420x740")
        self.root.configure(bg=BG_DARK)

        self.folder_path = tk.StringVar(value="No folder selected")
        self.files = []              # original filenames in folder
        self.preview_pairs = []      # (old_name, new_name)
        self.last_rename_log = []    # for undo: (new_path, old_path)

        self.mode = tk.StringVar(value="prefix")
        self.text_input = tk.StringVar()
        self.find_input = tk.StringVar()
        self.replace_input = tk.StringVar()
        self.start_num = tk.StringVar(value="1")
        self.digits = tk.StringVar(value="2")
        self.new_ext = tk.StringVar()
        self.case_mode = tk.StringVar(value="lower")

        self._build_ui()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        self._build_scrollable_root()
        self._build_header()
        self._build_folder_section()
        self._build_mode_section()
        self._build_options_section()
        self._build_action_buttons()
        self._build_preview_section()
        self._build_status_bar()

    def _build_scrollable_root(self):
        container = tk.Frame(self.root, bg=BG_DARK)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg=BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg=BG_DARK)

        window_id = canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(event):
            # keep inner frame exactly as wide as the visible canvas
            canvas.itemconfig(window_id, width=event.width)

        self.scroll_frame.bind("<Configure>", _on_frame_configure)
        canvas.bind("<Configure>", _on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # mouse wheel support (desktop testing)
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def _build_header(self):
        header = tk.Frame(self.scroll_frame, bg=BG_DARK)
        header.pack(fill="x", padx=20, pady=(24, 10))

        title = tk.Label(header, text="Bulk File Renamer", font=FONT_TITLE,
                          fg=ACCENT_2, bg=BG_DARK)
        title.pack(anchor="w")

        subtitle = tk.Label(header, text="Rename many files at once — fast & safe",
                             font=FONT_SUB, fg=TEXT_DIM, bg=BG_DARK)
        subtitle.pack(anchor="w", pady=(2, 0))

        # accent divider
        divider = tk.Canvas(header, height=3, bg=BG_DARK, highlightthickness=0)
        divider.pack(fill="x", pady=(12, 0))
        divider.bind("<Configure>", lambda e: self._draw_gradient_line(divider))

    def _draw_gradient_line(self, canvas):
        canvas.delete("all")
        w = canvas.winfo_width()
        colors = [ACCENT_1, ACCENT_PINK, ACCENT_PURPLE, ACCENT_CYAN]
        segment = max(w // len(colors), 1)
        for i, c in enumerate(colors):
            canvas.create_rectangle(i * segment, 0, (i + 1) * segment, 3, fill=c, outline=c)

    def _card(self, parent, pady=(0, 16)):
        wrapper = tk.Frame(parent, bg=BG_DARK)
        wrapper.pack(fill="x", padx=20, pady=pady)
        card = RoundedFrame(wrapper, color=BG_CARD, radius=16, height=1)
        card.pack(fill="x")
        inner = tk.Frame(card, bg=BG_CARD)
        card.create_window(0, 0, window=inner, anchor="nw", tags="inner")

        def _resize(event):
            card.itemconfig("inner", width=event.width)
            card._redraw()
            self.root.after(1, lambda: card.configure(height=inner.winfo_reqheight()))

        card.bind("<Configure>", _resize)
        inner.bind("<Configure>", lambda e: card.configure(height=inner.winfo_reqheight()))
        return inner

    def _build_folder_section(self):
        card = self._card(self.scroll_frame)
        pad = tk.Frame(card, bg=BG_CARD)
        pad.pack(fill="x", padx=16, pady=14)

        tk.Label(pad, text="FOLDER", font=FONT_LABEL, fg=ACCENT_CYAN, bg=BG_CARD).pack(anchor="w")
        self.folder_label = tk.Label(pad, textvariable=self.folder_path, font=FONT_NORMAL,
                                      fg=TEXT_DIM, bg=BG_CARD, wraplength=340, justify="left")
        self.folder_label.pack(anchor="w", pady=(4, 10))

        btn_row = tk.Frame(pad, bg=BG_CARD)
        btn_row.pack(fill="x")
        btn_row.columnconfigure(0, weight=2)
        btn_row.columnconfigure(1, weight=1)

        choose_btn = GradientButton(btn_row, "Choose Folder", self.choose_folder,
                                     color=ACCENT_CYAN, width=1, height=40)
        choose_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        refresh_btn = GradientButton(btn_row, "Refresh", self.load_files,
                                      color=ACCENT_PURPLE, width=1, height=40)
        refresh_btn.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        def _resize_folder_row(event):
            total = event.width - 6
            w1 = max(int(total * 0.6), 80)
            w2 = max(total - w1, 60)
            choose_btn.width = w1
            refresh_btn.width = w2
            choose_btn.configure(width=w1)
            refresh_btn.configure(width=w2)
            choose_btn._draw("normal")
            refresh_btn._draw("normal")
        btn_row.bind("<Configure>", _resize_folder_row)

    def _build_mode_section(self):
        card = self._card(self.scroll_frame)
        pad = tk.Frame(card, bg=BG_CARD)
        pad.pack(fill="x", padx=16, pady=14)

        tk.Label(pad, text="RENAME MODE", font=FONT_LABEL, fg=ACCENT_2, bg=BG_CARD).pack(anchor="w", pady=(0, 8))

        modes = [
            ("prefix", "Add Prefix"),
            ("suffix", "Add Suffix"),
            ("replace", "Find & Replace"),
            ("sequence", "Sequential Numbering"),
            ("extension", "Change Extension"),
            ("case", "Upper / Lower Case"),
        ]

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Glass.TRadiobutton", background=BG_CARD, foreground=TEXT_MAIN,
                         font=FONT_NORMAL)
        style.map("Glass.TRadiobutton",
                  background=[("active", BG_CARD)],
                  foreground=[("selected", ACCENT_1)])

        for value, label in modes:
            rb = ttk.Radiobutton(pad, text=label, value=value, variable=self.mode,
                                  style="Glass.TRadiobutton", command=self._refresh_options)
            rb.pack(anchor="w", pady=2)

    def _build_options_section(self):
        self.options_wrapper = tk.Frame(self.scroll_frame, bg=BG_DARK)
        self.options_wrapper.pack(fill="x", padx=20, pady=(0, 16))
        self._refresh_options()

    def _styled_entry(self, parent, textvariable, width=None):
        e = tk.Entry(parent, textvariable=textvariable, font=FONT_NORMAL,
                     bg="#12121e", fg=TEXT_MAIN, insertbackground=ACCENT_2,
                     relief="flat", highlightthickness=1,
                     highlightbackground=ACCENT_PURPLE, highlightcolor=ACCENT_1)
        if width:
            e.configure(width=width)
        return e

    def _refresh_options(self):
        for w in self.options_wrapper.winfo_children():
            w.destroy()

        card = RoundedFrame(self.options_wrapper, color=BG_PANEL, radius=16)
        card.pack(fill="x")
        inner = tk.Frame(card, bg=BG_PANEL)
        card.create_window(0, 0, window=inner, anchor="nw", tags="inner")

        def _resize(event):
            card.itemconfig("inner", width=event.width)
            card._redraw()
            self.root.after(1, lambda: card.configure(height=inner.winfo_reqheight()))

        card.bind("<Configure>", _resize)
        inner.bind("<Configure>", lambda e: card.configure(height=inner.winfo_reqheight()))

        pad = tk.Frame(inner, bg=BG_PANEL)
        pad.pack(fill="x", padx=16, pady=14)

        mode = self.mode.get()

        if mode == "prefix":
            tk.Label(pad, text="Prefix text", font=FONT_LABEL, fg=ACCENT_1, bg=BG_PANEL).pack(anchor="w")
            self._styled_entry(pad, self.text_input).pack(fill="x", pady=(6, 0))

        elif mode == "suffix":
            tk.Label(pad, text="Suffix text (before extension)", font=FONT_LABEL,
                      fg=ACCENT_1, bg=BG_PANEL).pack(anchor="w")
            self._styled_entry(pad, self.text_input).pack(fill="x", pady=(6, 0))

        elif mode == "replace":
            tk.Label(pad, text="Find", font=FONT_LABEL, fg=ACCENT_1, bg=BG_PANEL).pack(anchor="w")
            self._styled_entry(pad, self.find_input).pack(fill="x", pady=(6, 10))
            tk.Label(pad, text="Replace with", font=FONT_LABEL, fg=ACCENT_1, bg=BG_PANEL).pack(anchor="w")
            self._styled_entry(pad, self.replace_input).pack(fill="x", pady=(6, 0))

        elif mode == "sequence":
            tk.Label(pad, text="Base name", font=FONT_LABEL, fg=ACCENT_1, bg=BG_PANEL).pack(anchor="w")
            self._styled_entry(pad, self.text_input).pack(fill="x", pady=(6, 10))
            row = tk.Frame(pad, bg=BG_PANEL)
            row.pack(fill="x")
            col1 = tk.Frame(row, bg=BG_PANEL)
            col1.pack(side="left", expand=True, fill="x", padx=(0, 6))
            tk.Label(col1, text="Start #", font=FONT_LABEL, fg=ACCENT_1, bg=BG_PANEL).pack(anchor="w")
            self._styled_entry(col1, self.start_num).pack(fill="x", pady=(6, 0))
            col2 = tk.Frame(row, bg=BG_PANEL)
            col2.pack(side="left", expand=True, fill="x", padx=(6, 0))
            tk.Label(col2, text="Digits", font=FONT_LABEL, fg=ACCENT_1, bg=BG_PANEL).pack(anchor="w")
            self._styled_entry(col2, self.digits).pack(fill="x", pady=(6, 0))

        elif mode == "extension":
            tk.Label(pad, text="New extension (e.g. txt)", font=FONT_LABEL,
                      fg=ACCENT_1, bg=BG_PANEL).pack(anchor="w")
            self._styled_entry(pad, self.new_ext).pack(fill="x", pady=(6, 0))

        elif mode == "case":
            tk.Label(pad, text="Convert filename to:", font=FONT_LABEL, fg=ACCENT_1, bg=BG_PANEL).pack(anchor="w", pady=(0, 6))
            style = ttk.Style()
            style.configure("Glass.TRadiobutton", background=BG_PANEL, foreground=TEXT_MAIN, font=FONT_NORMAL)
            ttk.Radiobutton(pad, text="lowercase", value="lower", variable=self.case_mode,
                             style="Glass.TRadiobutton", command=self.preview_rename).pack(anchor="w")
            ttk.Radiobutton(pad, text="UPPERCASE", value="upper", variable=self.case_mode,
                             style="Glass.TRadiobutton", command=self.preview_rename).pack(anchor="w")
            ttk.Radiobutton(pad, text="Title Case", value="title", variable=self.case_mode,
                             style="Glass.TRadiobutton", command=self.preview_rename).pack(anchor="w")

        for var in (self.text_input, self.find_input, self.replace_input,
                    self.start_num, self.digits, self.new_ext):
            var.trace_add("write", lambda *a: self.preview_rename())

    def _build_action_buttons(self):
        row = tk.Frame(self.scroll_frame, bg=BG_DARK)
        row.pack(fill="x", padx=20, pady=(0, 16))
        row.columnconfigure(0, weight=1)
        row.columnconfigure(1, weight=1)

        preview_btn = GradientButton(row, "Preview", self.preview_rename,
                                      color=ACCENT_CYAN, width=1, height=44)
        preview_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        apply_btn = GradientButton(row, "Apply Rename", self.apply_rename,
                                    color=SUCCESS, width=1, height=44)
        apply_btn.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        def _resize_split(event):
            half = max((event.width - 12) // 2, 60)
            preview_btn.width = half
            apply_btn.width = half
            preview_btn.configure(width=half)
            apply_btn.configure(width=half)
            preview_btn._draw("normal")
            apply_btn._draw("normal")
        row.bind("<Configure>", _resize_split)

        row2 = tk.Frame(self.scroll_frame, bg=BG_DARK)
        row2.pack(fill="x", padx=20, pady=(0, 16))
        undo_btn = GradientButton(row2, "Undo Last Batch", self.undo_rename,
                                   color=DANGER, width=1, height=40)
        undo_btn.pack(fill="x")

        def _resize_undo(event):
            undo_btn.width = event.width
            undo_btn.configure(width=event.width)
            undo_btn._draw("normal")
        row2.bind("<Configure>", _resize_undo)

    def _build_preview_section(self):
        card = self._card(self.scroll_frame, pady=(0, 20))
        pad = tk.Frame(card, bg=BG_CARD)
        pad.pack(fill="x", padx=16, pady=14)

        tk.Label(pad, text="PREVIEW", font=FONT_LABEL, fg=ACCENT_PINK, bg=BG_CARD).pack(anchor="w", pady=(0, 8))

        self.preview_list = tk.Text(pad, height=14, bg="#12121e", fg=TEXT_MAIN,
                                     font=("Courier", 9), relief="flat",
                                     highlightthickness=1, highlightbackground=ACCENT_PURPLE,
                                     wrap="none")
        self.preview_list.pack(fill="both", expand=True)
        self.preview_list.insert("1.0", "Choose a folder to begin...")
        self.preview_list.configure(state="disabled")

    def _build_status_bar(self):
        self.status_var = tk.StringVar(value="Ready")
        status = tk.Label(self.scroll_frame, textvariable=self.status_var, font=FONT_SUB,
                           fg=TEXT_DIM, bg=BG_DARK)
        status.pack(fill="x", padx=20, pady=(0, 20))

    # -------------------------------------------------------------- Logic
    def choose_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_path.set(path)
            self.load_files()

    def load_files(self):
        path = self.folder_path.get()
        if not path or path == "No folder selected" or not os.path.isdir(path):
            messagebox.showwarning("No folder", "Please choose a valid folder first.")
            return
        try:
            self.files = sorted([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        self.status_var.set(f"Loaded {len(self.files)} file(s).")
        self.preview_rename()

    def _compute_new_name(self, filename, index):
        name, ext = os.path.splitext(filename)
        mode = self.mode.get()

        if mode == "prefix":
            return f"{self.text_input.get()}{filename}"

        elif mode == "suffix":
            return f"{name}{self.text_input.get()}{ext}"

        elif mode == "replace":
            find = self.find_input.get()
            repl = self.replace_input.get()
            if not find:
                return filename
            return filename.replace(find, repl)

        elif mode == "sequence":
            try:
                start = int(self.start_num.get())
            except ValueError:
                start = 1
            try:
                digits = int(self.digits.get())
            except ValueError:
                digits = 2
            base = self.text_input.get() or "file"
            num = str(start + index).zfill(digits)
            return f"{base}_{num}{ext}"

        elif mode == "extension":
            new_ext = self.new_ext.get().strip().lstrip(".")
            if not new_ext:
                return filename
            return f"{name}.{new_ext}"

        elif mode == "case":
            case_mode = self.case_mode.get()
            if case_mode == "lower":
                return filename.lower()
            elif case_mode == "upper":
                return filename.upper()
            elif case_mode == "title":
                return f"{name.title()}{ext}"

        return filename

    def preview_rename(self, *_):
        if not self.files:
            return
        self.preview_pairs = []
        for i, f in enumerate(self.files):
            new_name = self._compute_new_name(f, i)
            self.preview_pairs.append((f, new_name))

        self.preview_list.configure(state="normal")
        self.preview_list.delete("1.0", "end")
        for old, new in self.preview_pairs:
            marker = "→" if old != new else "="
            self.preview_list.insert("end", f"{old}\n   {marker} {new}\n\n")
        self.preview_list.configure(state="disabled")
        self.status_var.set(f"Preview ready — {len(self.preview_pairs)} file(s).")

    def apply_rename(self):
        if not self.preview_pairs:
            messagebox.showinfo("Nothing to rename", "Load a folder and set a rename mode first.")
            return

        folder = self.folder_path.get()
        confirm = messagebox.askyesno("Confirm Rename",
                                       f"Rename {len(self.preview_pairs)} file(s) in:\n{folder}\n\nContinue?")
        if not confirm:
            return

        self.last_rename_log = []
        errors = []
        renamed_count = 0

        for old, new in self.preview_pairs:
            if old == new:
                continue
            old_path = os.path.join(folder, old)
            new_path = os.path.join(folder, new)
            if os.path.exists(new_path):
                errors.append(f"{new} already exists, skipped")
                continue
            try:
                os.rename(old_path, new_path)
                self.last_rename_log.append((new_path, old_path))
                renamed_count += 1
            except Exception as e:
                errors.append(f"{old}: {e}")

        msg = f"Renamed {renamed_count} file(s)."
        if errors:
            msg += f"\n\n{len(errors)} skipped:\n" + "\n".join(errors[:10])
        messagebox.showinfo("Done", msg)
        self.status_var.set(f"Renamed {renamed_count} file(s). {len(errors)} skipped.")
        self.load_files()

    def undo_rename(self):
        if not self.last_rename_log:
            messagebox.showinfo("Nothing to undo", "No rename batch to undo.")
            return
        confirm = messagebox.askyesno("Undo", f"Undo last {len(self.last_rename_log)} rename(s)?")
        if not confirm:
            return
        undone = 0
        for new_path, old_path in reversed(self.last_rename_log):
            try:
                if os.path.exists(new_path) and not os.path.exists(old_path):
                    os.rename(new_path, old_path)
                    undone += 1
            except Exception:
                pass
        self.last_rename_log = []
        messagebox.showinfo("Undo Complete", f"Restored {undone} file(s).")
        self.status_var.set(f"Undo complete — {undone} file(s) restored.")
        self.load_files()


def main():
    root = tk.Tk()
    app = BulkRenamerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
