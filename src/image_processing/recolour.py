import cv2
import numpy as np

try:
    from . import utilities
except ImportError:
    import utilities


def add_recolour_arguments(subparsers, parent):
    p = subparsers.add_parser(
        "recolour",
        help="Apply colour transformations to an image (HSV-based)",
        parents=[parent],
    )
    p.add_argument("-s", "--source", type=utilities.valid_file, required=True, help="Source image")
    p.add_argument("-d", "--destination", help="Destination image")

    p.add_argument("--hue-shift", type=int, default=0, help="Hue shift in degrees (-180..180)")
    p.add_argument("--sat-mult", type=float, default=1.0, help="Saturation multiplier (0..3)")
    p.add_argument("--val-mult", type=float, default=1.0, help="Value/Brightness multiplier (0..3)")
    p.add_argument("--mode", choices=["hsv", "grayscale", "colorize"], default="hsv", help="Recolour mode")

def validate_recolour_arguments(args):
    # numeric validation
    if not isinstance(args.hue_shift, int):
        raise TypeError("hue-shift must be an integer")
    if args.hue_shift < -180 or args.hue_shift > 180:
        utilities.error("hue-shift must be between -180 and 180.")

    if not isinstance(args.sat_mult, (int, float)):
        raise TypeError("sat-mult must be a number")
    if args.sat_mult < 0 or args.sat_mult > 3:
        utilities.error("sat-mult must be between 0 and 3.")

    if not isinstance(args.val_mult, (int, float)):
        raise TypeError("val-mult must be a number")
    if args.val_mult < 0 or args.val_mult > 3:
        utilities.error("val-mult must be between 0 and 3.")

    # file validation + destination handling
    args.source = utilities.normalize_source(args.source)
    utilities.validate_supported_format(args.source, "source")

    args.destination = utilities.prepare_destination(
        args.destination,
        args.source,
        "_recoloured" + args.source.suffix,
    )
    utilities.validate_supported_format(args.destination, "destination")


def recolour_image(args):
    img = cv2.imread(str(args.source))
    if img is None:
        utilities.error(f"Failed to read the source image: {args.source}")

    # grayscale mode
    if args.mode == "grayscale":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        out_img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    # pseudo-color mode
    elif args.mode == "colorize":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        out_img = cv2.applyColorMap(gray, cv2.COLORMAP_JET)

    # default HSV recolour mode
    else:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)

        hue_delta = int(round(args.hue_shift / 2))
        h = (h.astype(np.int16) + hue_delta) % 180
        h = h.astype(np.uint8)

        s = np.clip(s.astype(np.float32) * args.sat_mult, 0, 255).astype(np.uint8)
        v = np.clip(v.astype(np.float32) * args.val_mult, 0, 255).astype(np.uint8)

        out_img = cv2.cvtColor(cv2.merge([h, s, v]), cv2.COLOR_HSV2BGR)

    out_path = utilities.givecorrectdestination(args.destination, args.force)

    ok = cv2.imwrite(str(out_path), out_img)
    if not ok:
        utilities.error(f"Failed to write the output image: {out_path}")

    print(f"\033[32mImage recoloured successfully: {out_path}\033[0m")