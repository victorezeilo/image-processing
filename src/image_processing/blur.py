# src/image_processing/blur.py
import sys
import argparse
import pathlib
import cv2

MAX_KERNEL = 99

def unique_path(path: pathlib.Path) -> pathlib.Path:
    """Return a non-existing path by appending _1, _2, ... if needed."""
    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    for i in range(1, 128):
        candidate = parent / f"{stem}_{i}{suffix}"
        if not candidate.exists():
            return candidate
    raise RuntimeError("Could not create a unique output filename (too many collisions).")


def valid_file(path: str) -> pathlib.Path:
    p = pathlib.Path(path).expanduser()
    if not p.is_file():
        raise argparse.ArgumentTypeError(f"{path} is not a valid file")
    return p


def add_blur_parser(subparsers):
    """Register the 'blur' subcommand."""
    blur_parser = subparsers.add_parser("blur", help="Blur an image (Gaussian blur)")
    blur_parser.add_argument("-s", "--source", type=valid_file, required=True, help="Source image")
    blur_parser.add_argument("-d", "--destination", help="Destination image (optional).")
    blur_parser.add_argument(
        "-k", "--kernel",
        type=int,
        default=15,
        help="Blur kernel size (odd integer, 1..99). Default: 15"
    )


def validate_blur_args(args):
    # Validate kernel
    if args.kernel is None:
        sys.exit("Error: kernel must be specified.")
    if not isinstance(args.kernel, int):
        sys.exit("Error: kernel must be an integer.")
    if args.kernel < 1 or args.kernel > MAX_KERNEL:
        sys.exit(f"Error: kernel must be between 1 and {MAX_KERNEL}.")
    if args.kernel % 2 == 0:
        sys.exit("Error: kernel must be an odd integer (e.g., 5, 11, 21).")

    # Resolve source
    args.source = pathlib.Path(args.source).expanduser().resolve()
    if not args.source.is_file():
        sys.exit(f"Source file does not exist: {args.source}")

    # Destination default: source_stem_blurred.<same suffix>
    if args.destination:
        args.destination = pathlib.Path(args.destination).expanduser()
    else:
        args.destination = args.source.with_name(f"{args.source.stem}_blurred{args.source.suffix}")

    args.destination = args.destination.resolve()
    args.destination.parent.mkdir(parents=True, exist_ok=True)

    # If destination exists and not --force, write to a unique path
    if args.destination.exists() and not getattr(args, "force", False):
        args.destination = unique_path(args.destination)


def blur_image(args):
    img = cv2.imread(str(args.source))
    if img is None:
        sys.exit(f"Error: could not read image file: {args.source}")

    blurred = cv2.GaussianBlur(img, (args.kernel, args.kernel), 0)

    ok = cv2.imwrite(str(args.destination), blurred)
    if not ok:
        sys.exit(f"Error: could not write output image to: {args.destination}")

    print(f"\033[32mImage Blured successfully")
    