import sys
import argparse
import cv2
import pathlib

try:
    # Running as a module: python -m src.image_processing.main
    from . import resize, convert, utilities, sharpen, recolour
except ImportError:
    # Running as a script: python src/image_processing/main.py
    import os
    import sys
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.image_processing import resize, convert, utilities, sharpen, recolour

# Main here
parser = argparse.ArgumentParser()
common = utilities.generalargs()
subparsers = parser.add_subparsers(dest='command')
convert.parseimageconversionargs(subparsers, common)
resize.add_resize_arguments(subparsers, common)
blur.add_blur_parser(subparsers)
sharpen.add_sharpen_arguments(subparsers, common)
recolour.add_recolour_arguments(subparsers, common)
args = parser.parse_args()

def main():
    if args.command is None:
        sys.exit("Please provide some arguments.")
    match args.command:
        case 'convert':
            convert.validatecommandsandconvert(args)  # Easier for now to have it in one function
        case 'resize':
            resize.validate_resize_arguments(args)
            resize.resize_image(args)
        case "blur":
            blur.validate_blur_args(args)
            blur.blur_image(args)
        case "sharpen":
            sharpen.validate_sharpen_arguments(args)
            sharpen.sharpen_image(args)
        case "recolour":
            recolour.validate_recolour_arguments(args)
            recolour.recolour_image(args)
        case _:
            print("Argument not recognized.")

if __name__ == "__main__":
    main()