#Adjust image resolution

# Checklist 
# The user can specify target width and height 
# The output image matches the requested resolution. 
# Error messages are displayed for invalid dimension.

import sys
import argparse
import pathlib
import cv2


MAX_DIMENSION = 4096


def unique_path(path: pathlib.Path) -> pathlib.Path:
    """Return a non-existing path by appending _1, _2, etc. if needed."""
    if not path.exists():
        return path
    
    # Append an index to the filename until a unique path is found
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    max_iterations = 127
    for i in range(1, max_iterations):
        candidate = parent / f"{stem}_{i}{suffix}"
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Could not find a unique path after {max_iterations} attempts: {path}")

def valid_file(path: str) -> pathlib.Path:
    """Validate that the given path is a file and return it as a Path object."""
    p = pathlib.Path(path)
    if not p.is_file():
        raise argparse.ArgumentTypeError(f"{path} is not a valid file")
    return p

def add_resize_arguments(subparsers):
    """Add arguments for the resize command."""
    resize_parser = subparsers.add_parser('resize', help='Resize an image to specified dimensions')
    resize_parser.add_argument('-s', '--source', type=valid_file, required=True, help='Source image')
    resize_parser.add_argument('-d', '--destination', help='Destination image.')
    resize_parser.add_argument('--width', type=int, required=True, help='Target width of the output image')
    resize_parser.add_argument('--height', type=int, required=True, help='Target height of the output image')
    
def validate_resize_arguments(args):
    """Validate the resize arguments."""
    if args.width <= 0 or args.height <= 0:
        raise ValueError("Width and height must be positive integers.")
    if args.width > MAX_DIMENSION or args.height > MAX_DIMENSION:
        raise ValueError(f"Width and height must not exceed {MAX_DIMENSION}.")
    
    # validate source path
    args.source = pathlib.Path(args.source).expanduser().resolve()
    if not args.source.is_file():
        sys.exit(f"Source file does not exist: {args.source}")
        
    # determine output path, if not provided, create a default one based on the source filename
    if args.destination:
        args.destination = pathlib.Path(args.destination).expanduser()
    else:
        args.destination = args.source.with_name(args.source.stem + '_resized' + args.source.suffix)

    args.destination = args.destination.resolve()
    args.destination.parent.mkdir(parents=True, exist_ok=True)
    
    # ensure the destination path is unique if it already exists. If --force is not specified, we will generate a unique path.
    if args.destination.exists() and not getattr(args, 'force', False):
        args.destination = unique_path(args.destination)
        

def resize_image(args):
    """Resize the image to the specified dimensions."""
    img = cv2.imread(str(args.source))
    if img is None:
        sys.exit(f"Failed to read the source image: {args.source}")
    
    # choose interpolation: area for shrinking, linear for enlarging
    h, w = img.shape[:2]
    if args.width < w and args.height < h:
        interp = cv2.INTER_AREA
    else:
        interp = cv2.INTER_LINEAR
    
    resized_img = cv2.resize(img, (args.width, args.height), interpolation=interp)
    
    ok = cv2.imwrite(str(args.destination), resized_img)
    if not ok:
        sys.exit(f"Failed to write the output image: {args.destination}")
    
    print(f"Image resized successfully: {args.destination} ({args.width}x{args.height})")