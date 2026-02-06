import sys
import argparse
import cv2
import pathlib
from . import utilities
from . import globals

def convertimage(args):
    realDest = utilities.givecorrectdestination(args.destination, args.force)
    img = cv2.imread(args.source)
    cv2.imwrite(realDest, img, [args.format, args.compression])

def validateimageconversioncommands(args):
    #VALIDATE INPUT
    formatImg = utilities.determineformat(args)
    inputFormat = formatImg
    match inputFormat:
        case 'png':
            inputFormat = cv2.IMWRITE_PNG_COMPRESSION
        case 'tiff':
            inputFormat = cv2.IMWRITE_TIFF_COMPRESSION
        case 'jpg' | 'jpeg':
            inputFormat = cv2.IMWRITE_JPEG_QUALITY
        case _:
            inputFormat = cv2.IMWRITE_PNG_COMPRESSION #PNG IS DEFAULT
    if formatImg is None: #PNG IS DEFAULT
        formatImg = 'png'
    args.source = pathlib.Path(args.source).expanduser().resolve()
    if not args.source.is_file():
        sys.exit(f"Source file does not exist: {args.source}")
    if args.destination:
        args.destination = pathlib.Path(args.destination).expanduser()
    else:
        args.destination = args.source.with_suffix(f".{formatImg}")
    args.destination = args.destination.resolve()
    args.destination.parent.mkdir(parents=True, exist_ok=True)
    args.format = inputFormat

def parseimageconversionargs(subparsers):
    #IMAGE CONVERSION
    convert_parser = subparsers.add_parser('convert', help='Convert image format')
    convert_parser.add_argument('-s', '--source', type=utilities.valid_file, required=True, help='Source image')
    convert_parser.add_argument('-d', '--destination', help='Destination image.')
    convert_parser.add_argument('-f', '--format', choices=['png', 'jpg', 'jpeg', 'tiff'], help='Output format.')
    convert_parser.add_argument('-c', '--compression', type=int, choices=range(0, 10), metavar='[0-9]', default=3, help='Compression level (0–9)')
