# Bulk File Renamer

A colorful, dark-themed desktop tool for renaming many files at once. Built with Python and Tkinter, designed to run smoothly on **Pydroid 3** (Android) as well as desktop Python.

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-FF6A00?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Pydroid%203%20%7C%20Desktop-3EE6D8?style=for-the-badge&logo=android&logoColor=white)
![License](https://img.shields.io/badge/License-All%20Rights%20Reserved-FF4F6D?style=for-the-badge&logo=bookstack&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-3EE67E?style=for-the-badge&logo=checkmarx&logoColor=white)
![Maintainer](https://img.shields.io/badge/Maintainer-CODEX--M41NUL-8A5CFF?style=for-the-badge&logo=github&logoColor=white)

---

## Features

- 📁 Pick a folder and list all files instantly
- ✏️ Six rename modes:
  - Add Prefix
  - Add Suffix
  - Find & Replace
  - Sequential Numbering
  - Change Extension
  - Uppercase / Lowercase / Title Case
- 👀 Live preview before applying any changes
- ↩️ Undo the last rename batch
- 🎨 Dark UI with gradient-accent styling
- 📱 Scrollable layout, works well on small screens (Pydroid 3)

---

## Screenshots

*(Add your own screenshots here after running the app)*

```
[ screenshot-1.png ]   [ screenshot-2.png ]
```

---

## Requirements

- Python 3.x
- Tkinter (usually included with Python; on Pydroid 3, install the **Tkinter plugin** from the app)

No external pip packages are required — this app only uses the Python standard library.

---

## Installation

### 🖥️ Desktop (Windows / Linux / macOS)

**Step 1 — Check Python is installed**
```bash
python3 --version
```

**Step 2 — Clone this repository**
```bash
git clone https://github.com/M41NUL/bulk-file-renamer.git
```

**Step 3 — Move into the project folder**
```bash
cd bulk-file-renamer
```

**Step 4 — Run the app**
```bash
python3 bulk_file_renamer.py
```

---

### 📱 Android (Pydroid 3)

**Step 1 — Install Pydroid 3**

[![Get it on Google Play](https://img.shields.io/badge/Google_Play-Pydroid_3-414141?style=for-the-badge&logo=googleplay&logoColor=white)](https://play.google.com/store/apps/details?id=ru.iiec.pydroid3)

**Step 2 — Install the Tkinter plugin**
Open Pydroid 3 → **☰ Menu** → **Plugins** → search **"Tkinter"** → **Install**

**Step 3 — Get the script onto your phone**
Download or copy `bulk_file_renamer.py` to your device (via Telegram, USB, file manager, or `git clone` inside Pydroid's terminal).

**Step 4 — Open the file**
In Pydroid 3, tap **File** → **Open** → select `bulk_file_renamer.py`

**Step 5 — Run it**
Tap the **▶ Run** button at the bottom of the screen

---

## How to Use

1. **Launch the app** — the main window opens with a dark, gradient-accented UI.
2. **Choose a folder** — tap "Choose Folder" and select the directory containing the files you want to rename.
3. **Pick a rename mode** from the list:
   | Mode | What it does |
   |---|---|
   | Add Prefix | Adds text to the beginning of every filename |
   | Add Suffix | Adds text before the file extension |
   | Find & Replace | Replaces a substring in filenames |
   | Sequential Numbering | Renames files as `basename_01`, `basename_02`, etc. |
   | Change Extension | Changes the file extension for all files |
   | Upper/Lower/Title Case | Converts filenames to the chosen case |
4. **Fill in the options** for the selected mode (e.g. prefix text, find/replace values, starting number).
5. **Check the live preview** — it updates automatically and shows `old_name → new_name` for every file.
6. **Tap "Apply Rename"** — confirm the action, and the files will be renamed in place.
7. If something goes wrong, tap **"Undo Last Batch"** to restore the previous filenames.

> ⚠️ **Note:** Renaming is applied directly to files on disk. Always double-check the preview before applying, and consider backing up important files first.

---

## Project Structure

```
bulk-file-renamer/
├── bulk_file_renamer.py   # Main application file
└── README.md              # This file
```

---

## 👤 Developer

<table>
<tr>
<td>

**Md. Mainul Islam**
Brand: `CODEX-M41NUL`

[![GitHub](https://img.shields.io/badge/GitHub-M41NUL-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/M41NUL)
[![Telegram](https://img.shields.io/badge/Telegram-Contact-26A5E4?style=flat-square&logo=telegram&logoColor=white)](https://t.me/mdmainulislaminfo)
[![Email](https://img.shields.io/badge/Email-Contact-EA4335?style=flat-square&logo=gmail&logoColor=white)](mailto:devmainulislam@gmail.com)
[![WhatsApp](https://img.shields.io/badge/WhatsApp-Chat-25D366?style=flat-square&logo=whatsapp&logoColor=white)](https://wa.me/8801308850528)

</td>
</tr>
</table>

---

## License

© 2026 CODEX-M41NUL. All Rights Reserved.

This project is shared for personal and educational use. Please credit the original author if you reuse or modify this code.
