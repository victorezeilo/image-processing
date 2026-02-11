import sys
import argparse
import cv2
import pathlib
import resize
import convert
import utilities

#Main here
parser = argparse.ArgumentParser()
common = utilities.generalargs()
subparsers = parser.add_subparsers(dest='command')
convert.parseimageconversionargs(subparsers, common)
resize.add_resize_arguments(subparsers, common)
args = parser.parse_args()
def main():
    if args.command is None:
        sys.exit("Please provide some arguments.")
    match args.command:
        case 'convert':
            convert.validatecommandsandconvert(args) #Easier for now to have it in one function
        case 'resize':
            resize.validate_resize_arguments(args)
            resize.resize_image(args)
        case _:
            print("Argument not recognized.")

if __name__ == "__main__":
    main()
