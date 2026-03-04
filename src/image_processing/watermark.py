import cv2
import numpy as np

try:
    from . import utilities
except ImportError:
    import utilities

DEFAULT_POS = "bottom-right"
DEFAULT_OPACITY = 0.2
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

    p.add_argument("--color", default="255,255,255", help="Text color in RGB format, e.g., 255,0,0 for red")
    p.add_argument("--angle", type=float, default=0.0, help="Rotation angle in degrees (e.g., 45 or 135)")


def validate_watermark_arguments(args):
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

    if not isinstance(args.angle, (int, float)):
        raise TypeError("angle must be a number")

    # RGB to BGR
    try:
        r, g, b = map(int, args.color.split(','))
        if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
            raise ValueError
        args.color_bgr = (b, g, r)  # 翻转为 BGR
    except ValueError:
        utilities.error("Color must be in 'R,G,B' format (e.g., 255,0,0). Values must be 0-255.")

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

    x = max(0, min(x, w - tw))
    y = max(th, min(y, h))
    return x, y


def watermark_image(args):
    img = cv2.imread(str(args.source))
    if img is None:
        utilities.error(f"Failed to read the source image: {args.source}")

    h, w = img.shape[:2]

    text_canvas = np.zeros((h, w, 3), dtype=np.uint8)
    font = cv2.FONT_HERSHEY_SIMPLEX

    x, y = _compute_position(img, args.text, font, args.scale, DEFAULT_THICKNESS, args.pos, args.margin)

    cv2.putText(text_canvas, args.text, (x + 2, y + 2), font, args.scale, (0, 0, 0), DEFAULT_THICKNESS + 1, cv2.LINE_AA)
    cv2.putText(text_canvas, args.text, (x, y), font, args.scale, args.color_bgr, DEFAULT_THICKNESS, cv2.LINE_AA)

    if args.angle != 0:
        (tw, th), _ = cv2.getTextSize(args.text, font, args.scale, DEFAULT_THICKNESS)
        center_x = x + tw // 2
        center_y = y - th // 2

        rotation_matrix = cv2.getRotationMatrix2D((center_x, center_y), args.angle, 1.0)
        text_canvas = cv2.warpAffine(text_canvas, rotation_matrix, (w, h))

    mask = np.any(text_canvas != 0, axis=-1).astype(np.float32)
    mask = np.expand_dims(mask, axis=-1)

    out_img = img.astype(np.float32) * (1 - mask * args.opacity) + text_canvas.astype(np.float32) * (
                mask * args.opacity)
    out_img = np.clip(out_img, 0, 255).astype(np.uint8)

    out_path = utilities.givecorrectdestination(args.destination, args.force)

    ok = cv2.imwrite(str(out_path), out_img)
    if not ok:
        utilities.error(f"Failed to write the output image: {out_path}")

    print(f"\033[32mImage watermarked successfully: {out_path}\033[0m")