import cv2
import numpy as np

try:
    from . import utilities
except ImportError:
    # if run in a non-package context (rare), fall back
    import utilities


MAX_LEVEL = 15.0
MAX_RADIUS = 25


def add_sharpen_arguments(subparsers, parent):
    p = subparsers.add_parser(
        "sharpen",
        help="Sharpen an image (unsharp mask)",
        parents=[parent],
    )
    p.add_argument("-s", "--source", type=utilities.valid_file, required=True, help="Source image")
    p.add_argument("-d", "--destination", help="Destination image")
    p.add_argument("--level", type=float, default=1.0, help="Sharpening level (0.0 to 5.0)")
    p.add_argument("--radius", type=int, default=3, help="Radius (kernel size control, 1 to 25)")


def validate_sharpen_arguments(args):
    # Validate params
    if args.level is None or not isinstance(args.level, (int, float)):
        raise TypeError("level must be a number")
    if args.level < 0:
        utilities.error("Sharpen level must be >= 0.")
    if args.level > MAX_LEVEL:
        utilities.error(f"Sharpen level too high. Use <= {MAX_LEVEL} to avoid excessive noise.")

    if args.radius is None or not isinstance(args.radius, int):
        raise TypeError("radius must be an integer")
    if args.radius <= 0:
        utilities.error("Radius must be a positive integer.")
    if args.radius > MAX_RADIUS:
        utilities.error(f"Radius too large. Use <= {MAX_RADIUS}.")

    # Validate source format
    args.source = utilities.normalize_source(args.source)
    utilities.validate_supported_format(args.source, "source")

    # Prepare destination
    args.destination = utilities.prepare_destination(
        args.destination,
        args.source,
        "_sharpened" + args.source.suffix,
    )
    utilities.validate_supported_format(args.destination, "destination")


def sharpen_image(args):
    img = cv2.imread(str(args.source))
    if img is None:
        utilities.error(f"Failed to read the source image: {args.source}")

    # force odd kernel size
    k = args.radius if args.radius % 2 == 1 else args.radius + 1

    # Unsharp mask
    blurred = cv2.GaussianBlur(img, (k, k), 0)
    sharpened = cv2.addWeighted(img, 1.0 + float(args.level), blurred, -float(args.level), 0)

    # clip to avoid overflow artifacts
    sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)

    out = utilities.givecorrectdestination(args.destination, args.force)
    ok = cv2.imwrite(str(out), sharpened)
    if not ok:
        utilities.error(f"Failed to write the output image: {out}")

    print(f"\033[32mImage sharpened successfully: {out}\033[0m")