import sys
import argparse
import cv2
import pathlib
import resize
import convert
import utilities
import globals


#Main here
subparsers = globals.parser.add_subparsers(dest='command')
utilities.generalargs()
convert.parseimageconversionargs(subparsers)
resize.add_resize_arguments(subparsers)
args = globals.parser.parse_args()
def main():
    if args.command is None:
        sys.exit("Please provide some arguments.")
    match args.command:
        case 'convert':
            convert.validateimageconversioncommands(args)
            convert.convertimage(args)
        case 'resize':
            resize.validate_resize_arguments(args)
            resize.resize_image(args)
        case _:
            print("Argument not recognized.")

if __name__ == "__main__":
    main()
