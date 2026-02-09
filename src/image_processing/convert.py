import sys
import argparse
import cv2
import pathlib
from . import utilities
from . import globals

def convertimage(args):
    realDest = utilities.givecorrectdestination(args.destination, args.force)
    img = cv2.imread(args.source)
    ok = cv2.imwrite(realDest, img, [args.format, args.compression])
    if not ok:
        sys.exit(f"Failed to write image to {realDest}")
    print(f"Image converted successfully: {realDest})")

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
        args.destination = args.source.with_name(args.source.stem + "_converted." + formatImg)
    args.destination = args.destination.resolve()
    args.destination.parent.mkdir(parents=True, exist_ok=True)
    args.format = inputFormat
    COMPRESSION_MAP = {
            'png': {
                        'low': 1,
                        'medium': 5,
                        'high': 9,
                    },
            'jpg': {
                        'low': 95,
                        'medium': 85,
                        'high': 70,
                    },
            'jpeg': {
                        'low': 95,
                        'medium': 85,
                        'high': 70,
                    },
            'tiff': {
                        'low': 1,
                        'medium': 5,   # LZW
                        'high': 8,     # Deflate
                    }
    }
    args.compression = COMPRESSION_MAP[formatImg][args.compression]

def parseimageconversionargs(subparsers):
    #IMAGE CONVERSION
    convert_parser = subparsers.add_parser('convert', help='Convert image format')
    convert_parser.add_argument('-s', '--source', type=utilities.valid_file, required=True, help='Source image')
    convert_parser.add_argument('-d', '--destination', help='Destination image.')
    convert_parser.add_argument('-f', '--format', choices=['png', 'jpg', 'jpeg', 'tiff'], help='Output format.')
    LEVELS = ('low', 'medium', 'high')
    convert_parser.add_argument('-c', '--compression', choices=LEVELS, default='medium', help='Compression level (low, medium, high')
