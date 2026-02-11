import sys
import argparse
import cv2
import pathlib

SUPPORTED_FORMATS = {'png', 'jpg', 'jpeg', 'tiff'}

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
        sys.exit(f"\033[31m{msg}\033[0m")

def givecorrectdestination(dest, force):
    if dest.exists() and not force:
        return unique_path(dest)
    return dest

def determineformat(args):
    if args.format:
        return args.format
    if args.destination:
        return pathlib.Path(args.destination).suffix.lstrip('.')
    return None

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
