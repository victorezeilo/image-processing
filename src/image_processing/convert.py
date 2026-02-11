import sys
import argparse
import cv2
import pathlib
import utilities

def convertimage(args):
    realDest = utilities.givecorrectdestination(args.destination, args.force)
    img = cv2.imread(args.source)
    ok = cv2.imwrite(realDest, img, [args.format, args.compression])
    if not ok:
        utilities.error(f"Failed to write image to {realDest}")
    print(f"\033[32mImage converted successfully: {realDest} to the format {args.format}\033[0m")

def validateimageconversioncommands(args):
    #VALIDATE INPUT
    formatImg = utilities.determineformat(args)
    if formatImg is None: #PNG IS DEFAULT
        formatImg = 'png'

    utilities.validate_supported_format_string(formatImg, "format")

    inputFormat = formatImg
    match inputFormat:
        case 'png':
            inputFormat = cv2.IMWRITE_PNG_COMPRESSION
        case 'tiff':
            inputFormat = cv2.IMWRITE_TIFF_COMPRESSION
        case 'jpg' | 'jpeg':
            inputFormat = cv2.IMWRITE_JPEG_QUALITY
        case _:
            inputFormat = cv2.IMWRITE_PNG_COMPRESSION #SHOULD NOT HAPPEN ANYWAY

    args.source = utilities.normalize_source(args.source)
    utilities.validate_supported_format(args.source, "source")

    if args.destination:
        suffix = f".{formatImg}"
    else:
        suffix = f"_converted.{formatImg}"

    args.destination = utilities.prepare_destination(args.destination, args.source, suffix)
    utilities.validate_supported_format(args.source, "destination")

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

def parseimageconversionargs(subparsers, parent):
    #IMAGE CONVERSION
    convert_parser = subparsers.add_parser('convert', help='Convert image format', parents=[parent])
    convert_parser.add_argument('-s', '--source', type=utilities.valid_file, required=True, help='Source image')
    convert_parser.add_argument('-d', '--destination', help='Destination image.')
    convert_parser.add_argument('-f', '--format', help='Output format.')
    LEVELS = ('low', 'medium', 'high')
    convert_parser.add_argument('-c', '--compression', choices=LEVELS, default='medium', help='Compression level (low, medium, high')
