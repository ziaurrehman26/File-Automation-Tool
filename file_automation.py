import os
import shutil
import logging
from pathlib import Path
from datetime import datetime

# -------- Configuration --------
# Map of folder name -> list of extensions
FILE_TYPES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt"],
    "Spreadsheets": [".xls", ".xlsx", ".csv", ".ods"],
    "Presentations": [".ppt", ".pptx", ".odp"],
    "Videos": [".mp4", ".mkv", ".mov", ".avi", ".flv", ".wmv"],
    "Audio": [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Code": [".py", ".js", ".ts", ".html", ".css", ".java", ".c", ".cpp"],
    "Others": []  # fallback
}

def setup_logging(base_dir: Path) -> Path:
    """Create logs directory and configure logging."""
    logs_dir = base_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"file_organizer_{timestamp}.log"

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logging.info("Started file organization in %s", base_dir)
    return log_file

def get_category(extension: str) -> str:
    """Return folder/category name for a given file extension."""
    ext = extension.lower()
    for category, exts in FILE_TYPES.items():
        if exts and ext in exts:
            return category
    return "Others"

def move_file(src: Path, dest_dir: Path) -> Path:
    """
    Move a file to dest_dir, avoiding overwrites by renaming if needed.
    Returns final destination path.
    """
    dest_dir.mkdir(exist_ok=True)
    dest_path = dest_dir / src.name

    if not dest_path.exists():
        shutil.move(str(src), str(dest_path))
        return dest_path

    # If file exists, append _1, _2, ... before the suffix
    stem = dest_path.stem
    suffix = dest_path.suffix
    counter = 1
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = dest_dir / new_name
        if not new_path.exists():
            shutil.move(str(src), str(new_path))
            return new_path
        counter += 1

def organize_directory(target_dir: str, dry_run: bool = False) -> None:
    """
    Organize files in target_dir into subfolders by type.
    Logs all actions into a timestamped log file in target_dir/logs.
    """
    base_path = Path(target_dir).expanduser().resolve()
    if not base_path.is_dir():
        raise NotADirectoryError(f"{base_path} is not a valid directory")

    log_file = setup_logging(base_path)
    print(f"Logging to: {log_file}")

    for entry in base_path.iterdir():
        # Skip directories (including the logs folder)
        if entry.is_dir():
            continue

        if not entry.is_file():
            continue

        ext = entry.suffix
        category = get_category(ext)
        dest_dir = base_path / category
        dest_path = dest_dir / entry.name

        if dry_run:
            logging.info("[DRY-RUN] Would move '%s' -> '%s'", entry, dest_dir)
            print(f"[DRY-RUN] Would move: {entry.name} -> {category}/")
            continue

        final_path = move_file(entry, dest_dir)
        logging.info("Moved '%s' -> '%s'", entry, final_path)
        print(f"Moved: {entry.name} -> {final_path}")

    logging.info("Finished organizing directory: %s", base_path)
    print("Organization complete.")

if __name__ == "__main__":
    # Simple CLI usage: edit this path or prompt user
    folder = input("Enter the path of the folder to organize: ").strip()
    if not folder:
        print("No folder provided. Exiting.")
    else:
        # Set dry_run=True to test without actually moving files
        organize_directory(folder, dry_run=False)