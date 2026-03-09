import argparse
import sys

try:
    # package imports (when running: python -m src.image_processing.menu)
    from . import blur, sharpen, recolour, watermark, resize, convert, undo, utilities
except ImportError:
    # fallback (rare)
    import blur, sharpen, recolour, watermark, resize, convert, undo, utilities


def _ask_yes_no(prompt: str, default: bool = False) -> bool:
    d = "y" if default else "n"
    ans = (input(f"{prompt} (y/n) [{d}]: ").strip().lower() or d)
    return ans in ("y", "yes")


def _ask_optional(prompt: str) -> str | None:
    val = input(f"{prompt} (leave empty for default): ").strip()
    return val if val else None


def _run_safely(fn):
    try:
        fn()
    except Exception as e:
        print(f"\033[31mError: {e}\033[0m")


# -------------------- MENU ACTIONS --------------------

def run_blur():
    src = input("Source image path: ").strip()
    dst = _ask_optional("Destination path")
    kernel = int(input("Blur kernel [15]: ").strip() or "15")
    force = _ask_yes_no("Force overwrite?", default=False)

    args = argparse.Namespace(
        source=src,
        destination=dst,
        kernel=kernel,
        force=force,
    )
    blur.validate_blur_args(args)
    blur.blur_image(args)


def run_sharpen():
    src = input("Source image path: ").strip()
    dst = _ask_optional("Destination path")
    level = float(input("Sharpen level [1.5]: ").strip() or "1.5")
    radius = int(input("Sharpen radius [3]: ").strip() or "3")
    force = _ask_yes_no("Force overwrite?", default=False)

    args = argparse.Namespace(
        source=src,
        destination=dst,
        level=level,
        radius=radius,
        force=force,
    )
    sharpen.validate_sharpen_arguments(args)
    sharpen.sharpen_image(args)


def run_recolour():
    src = input("Source image path: ").strip()
    dst = _ask_optional("Destination path")
    mode = (input("Mode (hsv/grayscale/colorize) [hsv]: ").strip() or "hsv")
    hue_shift = int(input("Hue shift (-180..180) [0]: ").strip() or "0")
    sat_mult = float(input("Saturation multiplier (0..3) [1.0]: ").strip() or "1.0")
    val_mult = float(input("Value multiplier (0..3) [1.0]: ").strip() or "1.0")
    force = _ask_yes_no("Force overwrite?", default=False)

    args = argparse.Namespace(
        source=src,
        destination=dst,
        hue_shift=hue_shift,
        sat_mult=sat_mult,
        val_mult=val_mult,
        mode=mode,
        force=force,
    )
    recolour.validate_recolour_arguments(args)
    recolour.recolour_image(args)


def run_watermark():
    src = input("Source image path: ").strip()
    dst = _ask_optional("Destination path")
    text = input("Watermark text: ").strip()
    pos = (input("Position (top-left/top-right/bottom-left/bottom-right/center) [bottom-right]: ").strip()
           or "bottom-right")
    opacity = float(input("Opacity 0..1 [0.2]: ").strip() or "0.2")
    scale = float(input("Scale [1.0]: ").strip() or "1.0")
    margin = int(input("Margin [10]: ").strip() or "10")

    color = input("Color (R,G,B) [255,255,255 for white]: ").strip() or "255,255,255"
    angle = float(input("Rotation angle [0 for horizontal]: ").strip() or "0")

    force = _ask_yes_no("Force overwrite?", default=False)

    args = argparse.Namespace(
        source=src,
        destination=dst,
        text=text,
        pos=pos,
        opacity=opacity,
        scale=scale,
        margin=margin,
        color=color,
        angle=angle,
        force=force,
    )
    watermark.validate_watermark_arguments(args)
    watermark.watermark_image(args)


def run_resize():
    src = input("Source image path: ").strip()
    dst = _ask_optional("Destination path")
    width = int(input("Width: ").strip())
    height = int(input("Height: ").strip())
    force = _ask_yes_no("Force overwrite?", default=False)

    args = argparse.Namespace(
        source=src,
        destination=dst,
        width=width,
        height=height,
        force=force,
    )
    resize.validate_resize_arguments(args)
    resize.resize_image(args)


def run_convert():
    src = input("Source image path: ").strip()
    dst = _ask_optional("Destination path")
    fmt = (input("Format (png/jpg/jpeg/tiff) [png]: ").strip() or "png")
    compression = (input("Compression (low/medium/high) [medium]: ").strip() or "medium")
    force = _ask_yes_no("Force overwrite?", default=False)

    args = argparse.Namespace(
        source=src,
        destination=dst,
        format=fmt,
        compression=compression,
        force=force,
    )

    try:
        convert.validatecommandsandconvert(args)
    except SystemExit as e:
        raise ValueError(str(e) if str(e) else "Convert command failed")
    
def run_undo():
    target = input("File to undo (restore previous version): ").strip()
    args = argparse.Namespace(source=target)
    undo.undo_last(args)


# -------------------- MENU LOOP --------------------

def show_menu():
    print("\nImage Processing Tool")
    print("---------------------")
    print("1. Blur Image")
    print("2. Sharpen Image")
    print("3. Recolour Image")
    print("4. Watermark Image")
    print("5. Resize Image")
    print("6. Convert Image")
    print("7. Undo")
    print("8. Exit")


def main():
    while True:
        show_menu()
        choice = input("\nSelect option: ").strip()

        if choice == "1":
            _run_safely(run_blur)
        elif choice == "2":
            _run_safely(run_sharpen)
        elif choice == "3":
            _run_safely(run_recolour)
        elif choice == "4":
            _run_safely(run_watermark)
        elif choice == "5":
            _run_safely(run_resize)
        elif choice == "6":
            _run_safely(run_convert)
        elif choice == "7":
            _run_safely(run_undo)
        elif choice == "8":
            print("Exiting...")
            sys.exit(0)
        else:
            print("Invalid choice. Please choose 1-8.")


if __name__ == "__main__":
    main()
