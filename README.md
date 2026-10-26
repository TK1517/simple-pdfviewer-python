# Multi-User PDF Viewer Application

A desktop PDF viewer built with **Python**, **Tkinter**, and **CustomTkinter**. It lets users register and log in, open PDF files, navigate pages, adjust zoom, and save personal bookmarks for individual PDF documents. User accounts and bookmarks are stored locally in an SQLite database.

## Features

- **User accounts:** Register and log in with a username and password.
- **Multi-user bookmarks:** Each account has its own bookmarks.
- **Open PDF files:** Choose a PDF from your computer.
- **Page navigation:** Move to the previous or next page, or jump directly to a page number.
- **Bookmarks:** Add bookmarks, view saved bookmarks, jump to a bookmarked page, and delete selected bookmarks.
- **Zoom controls:** Zoom in and out using the buttons or `Ctrl` + mouse wheel.
- **Keyboard navigation:** Use the left and right arrow keys to change pages.
- **Persistent storage:** Store accounts and bookmarks in SQLite.
- **Customizable interface:** Use CustomTkinter widgets with background and application icon images.
- **Windows executable option:** Package the application with PyInstaller.

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| GUI | Tkinter, CustomTkinter |
| PDF rendering | PyMuPDF (`fitz`) |
| Image handling | Pillow (`PIL`) |
| Database | SQLite |
| Windows packaging | PyInstaller |

## Requirements

- Python 3.10 or a compatible Python version supported by the installed dependencies
- The image assets `app_icon.png` and `background_image.jpg`
- A Windows environment if you want to build or run the Windows `.exe` package

## Installation

### 1. Clone or download the project

```bash
git clone <repository-url>
cd <project-folder>
```

Replace `<repository-url>` and `<project-folder>` with your repository URL and directory name. Alternatively, download the source code and open a terminal in the project directory.

### 2. Create and activate a virtual environment (recommended)

**Windows — Command Prompt**
```bat
python -m venv .venv
.venv\Scripts\activate
```

**Windows — PowerShell**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install customtkinter pymupdf pillow pyinstaller
```

`tkinter` is included with most standard Windows Python installations. On some Linux distributions, it may need to be installed separately using the system package manager.

### 4. Check the required image assets

Ensure these files are in the same working directory as the Python script:

```text
app_icon.png
background_image.jpg
```

The current application loads both images at startup. If either file is missing or has an incompatible format, the application may fail to launch.

## Run the Application

Run the Python file containing the `PDFViewerApp` class. For example, if the file is named `main.py`:

```bash
python main.py
```

If your script has a different name, replace `main.py` with that filename.

## How to Use

1. **Register:** Enter a username and a password of at least six characters, then select **Register**.
2. **Log in:** Enter the same credentials and select **Login**.
3. **Open a PDF:** Select **Open PDF** and choose a PDF file.
4. **Navigate pages:** Use **Previous Page** or **Next Page**, or select **Go to Page** and enter a page number.
5. **Adjust zoom:** Use **Zoom In** and **Zoom Out**, or hold `Ctrl` while scrolling the mouse wheel.
6. **Save a bookmark:** Select **Bookmark Page** to save the current page for the open PDF.
7. **Manage bookmarks:** Select **View Bookmarks** to show or hide the list. Double-click a bookmark to open its page, or select a bookmark and choose **Delete Selected Bookmark** to remove it.
8. **Switch users:** Select **Switch Account** to return to the login screen.
9. **Exit:** Select **Quit** to close the application.

Bookmarks are associated with the logged-in user and the PDF file path. To access bookmarks later, open the same PDF from the same path while logged in to the same account.

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `←` Left Arrow | Go to the previous page |
| `→` Right Arrow | Go to the next page |
| `Ctrl` + Mouse Wheel Up | Zoom in |
| `Ctrl` + Mouse Wheel Down | Zoom out |

The mouse-wheel zoom binding depends on the mouse-wheel event format provided by the operating system and Tkinter.

## Database

The application creates an SQLite database named `pdf_viewer.db` in its current working directory. The tables are created automatically when the application starts.

- **`users`** — stores user IDs, usernames, and passwords.
- **`bookmarks`** — stores bookmark IDs, user IDs, PDF file paths, and zero-based page numbers.

The database persists between runs. Back up `pdf_viewer.db` if you want to preserve account and bookmark data.

### Security note

**This implementation stores passwords as plain text in SQLite.** It is suitable only as a learning or demonstration project in its current form. Do not use real or reused passwords. Before using this application for sensitive documents or real accounts, implement password hashing with a suitable password-hashing algorithm, improve account/data deletion handling, and review database access and file permissions.

## Build a Windows Executable

You can use PyInstaller to package the application. From the project directory, run:

```bash
python -m PyInstaller --noconfirm --windowed --onefile --name PDFViewer --add-data "app_icon.png;." --add-data "background_image.jpg;." main.py
```

Replace `main.py` with your actual script filename. The Windows `--add-data` separator is a semicolon (`;`). The executable will normally be created at:

```text
dist/PDFViewer.exe
```

### Important packaging note

The current source opens `app_icon.png`, `background_image.jpg`, and `pdf_viewer.db` using relative paths. A one-file executable may extract bundled assets to a temporary directory, and its current working directory may differ from the executable's location. For reliable packaging, update the code to resolve bundled assets using a PyInstaller-aware resource path and choose an explicit writable location for the database before building the executable.

PyInstaller bundles the Python runtime and dependencies needed by the packaged application, but the application should still be tested on a clean Windows machine.

## Suggested Project Structure

```text
multi-user-pdf-viewer/
├── main.py                 # Application source (use your actual filename)
├── app_icon.png            # Application icon
├── background_image.jpg    # Login/window background
├── pdf_viewer.db           # Created automatically at runtime
├── requirements.txt        # Optional dependency list
└── README.md
```

The names shown above are examples; keep the filenames consistent with your actual project.

### Optional `requirements.txt`

You can create a `requirements.txt` file containing:

```text
customtkinter
PyMuPDF
Pillow
pyinstaller
```

Tkinter is normally supplied by Python and is not installed through pip on standard Windows installations.

## Troubleshooting

- **`ModuleNotFoundError`:** Activate your virtual environment and install the dependencies listed above.
- **Missing image file:** Ensure `app_icon.png` and `background_image.jpg` exist in the expected working directory.
- **PDF fails to open:** Check that the file is a valid PDF and is accessible to your account.
- **Bookmarks do not appear:** Confirm that you are logged in to the correct account and opened the PDF from the same file path used when the bookmarks were created.
- **Executable cannot find assets or database:** Review the resource and database paths used by the packaged build; see the Windows executable section above.

## Future Improvements

Possible extensions include:

- Hash passwords instead of storing them as plain text.
- Add a password-reset or account-recovery workflow.
- Support recent files and reopening the last viewed document.
- Remember zoom level and last-read page per user and document.
- Add search within PDF text, page thumbnails, and document metadata.
- Improve database integrity, including cascading bookmark deletion when an account is deleted.
- Add automated tests and a reproducible release/build workflow.

## License

Add a license file (for example, an MIT License) if you intend to distribute or publish this project. No license is specified here, so usage and redistribution terms have not been assumed.
