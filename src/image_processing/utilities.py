import sys
import argparse
import cv2
import pathlib
import json
import shutil
from datetime import datetime

SUPPORTED_FORMATS = {'png', 'jpg', 'jpeg', 'tiff'}

# ---- UNDO / HISTORY SETTINGS ----
HISTORY_DIR = pathlib.Path(".history")
HISTORY_FILE = HISTORY_DIR / "history.json"


def unique_path(path):
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    max_iterations = 127
    i = 1
    while i < max_iterations:
        candidate = parent / f"{stem}_{i}{suffix}"
        if not candidate.exists():
            return candidate
        i += 1
    raise RuntimeError("Could not find a unique filename")


def normalize_source(path_str: str):
    path = pathlib.Path(path_str).expanduser().resolve()
    if not path.is_file():
        sys.exit(f"\033[31mSource file does not exist: {path}\033[0m")
    return path


def prepare_destination(dest_str: str | None, source: pathlib.Path, suffix: str):
    if dest_str:
        dest = pathlib.Path(dest_str).expanduser()
    else:
        dest = source.with_name(source.stem + suffix)
    dest = dest.resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)
    return dest


def error(msg):
    raise ValueError(msg)


# --------- UNDO HELPERS ----------
def _load_history() -> dict:
    HISTORY_DIR.mkdir(exist_ok=True)
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_history(history: dict) -> None:
    HISTORY_DIR.mkdir(exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")


def backup_before_overwrite(dest: pathlib.Path) -> None:
    """
    If destination exists and will be overwritten, copy it into .history/
    and record the backup path in .history/history.json
    """
    if not dest.exists() or not dest.is_file():
        return

    HISTORY_DIR.mkdir(exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup_name = f"{dest.stem}__{ts}{dest.suffix}"
    backup_path = (HISTORY_DIR / backup_name).resolve()

    shutil.copy2(dest, backup_path)

    history = _load_history()
    key = str(dest.resolve())
    history.setdefault(key, []).append(str(backup_path))
    _save_history(history)


def givecorrectdestination(dest, force):
    """
    Existing behavior:
    - If dest exists and not force -> create unique path
    - Else return dest

    Added behavior:
    - If dest exists and force -> back it up for undo
    """
    if dest.exists() and not force:
        return unique_path(dest)

    if dest.exists() and force:
        backup_before_overwrite(dest)

    return dest


def determineformat(args):
    if args.format:
        formatImg = args.format.lower()
        if args.destination:
            dest_ext = get_extension(args.destination)
            if dest_ext and dest_ext != formatImg:
                error(f"Destination extension '.{dest_ext}' does not match the format {formatImg}")
        return formatImg
    if args.destination:
        dest_ext = get_extension(args.destination)
        if dest_ext:
            return dest_ext.lower()
    return 'png'


def generalargs():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument('--force', action='store_true', help='Overwrite output file')
    return common


def valid_file(path):
    p = pathlib.Path(path)
    if not p.is_file():
        raise argparse.ArgumentTypeError(f"{path} is not a valid file")
    return p


def get_extension(path):
    path = pathlib.Path(path)
    return path.suffix.lower().lstrip('.')


def validate_supported_format_string(fmt, role):
    fmt = fmt.lower()
    if fmt not in SUPPORTED_FORMATS:
        error(f"\033[31mUnsupported {role} format: {fmt}\nSupported formats: {', '.join(sorted(SUPPORTED_FORMATS))}\033[0m")
    return fmt


def validate_supported_format(path, role):
    ext = get_extension(path)
    if ext not in SUPPORTED_FORMATS:
        error(f"\033[31mUnsupported {role} format: {ext}\nSupported formats: {', '.join(sorted(SUPPORTED_FORMATS))}\033[0m")
    return ext