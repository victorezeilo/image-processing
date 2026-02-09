import sys
import argparse
import cv2
import pathlib
from . import globals

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
    globals.parser.add_argument('--force', action='store_true', help='Overwrite output file')

def valid_file(path):
    p = pathlib.Path(path)
    if not p.is_file():
        raise argparse.ArgumentTypeError(f"{path} is not a valid file")
    return p
