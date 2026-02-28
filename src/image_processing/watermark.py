import cv2

try:
    from . import utilities
except ImportError:
    import utilities


DEFAULT_POS = "bottom-right"
DEFAULT_OPACITY = 0.35
DEFAULT_SCALE = 1.0
DEFAULT_MARGIN = 10
DEFAULT_THICKNESS = 2

VALID_POSITIONS = ["top-left", "top-right", "bottom-left", "bottom-right", "center"]


def add_watermark_arguments(subparsers, parent):
    p = subparsers.add_parser(
        "watermark",
        help="Add a text watermark to an image",
        parents=[parent],
    )
    p.add_argument("-s", "--source", type=utilities.valid_file, required=True, help="Source image")
    p.add_argument("-d", "--destination", help="Destination image")

    p.add_argument("--text", required=True, help="Watermark text")
    p.add_argument("--pos", choices=VALID_POSITIONS, default=DEFAULT_POS, help="Watermark position")
    p.add_argument("--opacity", type=float, default=DEFAULT_OPACITY, help="Opacity (0..1)")
    p.add_argument("--scale", type=float, default=DEFAULT_SCALE, help="Font scale")
    p.add_argument("--margin", type=int, default=DEFAULT_MARGIN, help="Margin in pixels")


def validate_watermark_arguments(args):
    # numeric validation
    if not isinstance(args.opacity, (int, float)):
        raise TypeError("opacity must be a number")
    if args.opacity < 0 or args.opacity > 1:
        utilities.error("opacity must be between 0 and 1.")

    if not isinstance(args.scale, (int, float)):
        raise TypeError("scale must be a number")
    if args.scale <= 0:
        utilities.error("scale must be greater than 0.")

    if not isinstance(args.margin, int):
        raise TypeError("margin must be an integer")
    if args.margin < 0:
        utilities.error("margin must be >= 0.")

    # file validation + destination handling (SAME AS recolour.py)
    args.source = utilities.normalize_source(args.source)
    utilities.validate_supported_format(args.source, "source")

    args.destination = utilities.prepare_destination(
        args.destination,
        args.source,
        "_watermarked" + args.source.suffix,
    )
    utilities.validate_supported_format(args.destination, "destination")


def _compute_position(img, text, font, scale, thickness, pos, margin):
    (tw, th), _ = cv2.getTextSize(text, font, scale, thickness)
    h, w = img.shape[:2]

    if pos == "top-left":
        x = margin
        y = margin + th
    elif pos == "top-right":
        x = w - margin - tw
        y = margin + th
    elif pos == "bottom-left":
        x = margin
        y = h - margin
    elif pos == "bottom-right":
        x = w - margin - tw
        y = h - margin
    else:  # center
        x = (w - tw) // 2
        y = (h + th) // 2

    # keep inside bounds
    x = max(0, min(x, w - tw))
    y = max(th, min(y, h))
    return x, y


def watermark_image(args):
    img = cv2.imread(str(args.source))
    if img is None:
        utilities.error(f"Failed to read the source image: {args.source}")

    overlay = img.copy()
    font = cv2.FONT_HERSHEY_SIMPLEX

    x, y = _compute_position(
        img,
        args.text,
        font,
        args.scale,
        DEFAULT_THICKNESS,
        args.pos,
        args.margin,
    )

    # draw text with small shadow for visibility
    cv2.putText(
        overlay,
        args.text,
        (x + 2, y + 2),
        font,
        args.scale,
        (0, 0, 0),
        DEFAULT_THICKNESS + 1,
        cv2.LINE_AA,
    )
    cv2.putText(
        overlay,
        args.text,
        (x, y),
        font,
        args.scale,
        (255, 255, 255),
        DEFAULT_THICKNESS,
        cv2.LINE_AA,
    )

    out_img = cv2.addWeighted(overlay, float(args.opacity), img, 1 - float(args.opacity), 0)

    out_path = utilities.givecorrectdestination(args.destination, args.force)

    ok = cv2.imwrite(str(out_path), out_img)
    if not ok:
        utilities.error(f"Failed to write the output image: {out_path}")

    print(f"\033[32mImage watermarked successfully: {out_path}\033[0m")