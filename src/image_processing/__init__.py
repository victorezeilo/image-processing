import sys
import argparse
import cv2
import pathlib

def unique_path(path):
    if not path.exists():
        return path
    stem = path.stemrun
    suffix = path.suffix
    parent = path.parent
    max_iterations = 127
    i = 1
    while i < max_iterations:
        candidate = parent / f"{stem}_{i}{suffix}"
        if not candidate.exists():
            return candidate
        i += 1

def givecorrectdestination(dest):
    if dest.exists() and not args.force:
        return unique_path(dest)
    return dest

def determineformat(args):
    if args.format:
        return args.format
    if args.destination:
        return pathlib.Path(args.destination).suffix.lstrip('.')
    return None

def convertimage(inputpath, outputpath, outputformat, compression):
    img = cv2.imread(inputpath)
    cv2.imwrite(outputpath, img, [outputformat, compression])

def generalargs():
    parser.add_argument('--force', action='store_true', help='Overwrite output file')

def valid_file(path):
    p = pathlib.Path(path)
    if not p.is_file():
        raise argparse.ArgumentTypeError(f"{path} is not a valid file")
    return p

def parseimageconversionargs():
    #IMAGE CONVERSION
    convert_parser = subparsers.add_parser('convert', help='Convert image format')
    convert_parser.add_argument('-s', '--source', type=valid_file, required=True, help='Source image')
    convert_parser.add_argument('-d', '--destination', help='Destination image.')
    convert_parser.add_argument('-f', '--format', choices=['png', 'jpg', 'jpeg', 'tiff'], help='Output format.')
    convert_parser.add_argument('-c', '--compression', type=int, choices=range(0, 10), metavar='[0-9]', default=3, help='Compression level (0–9)')

def validateimageconversioncommands(args):
    #VALIDATE INPUT
    formatImg = determineformat(args)
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

#Main here
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest='command')
generalargs()
parseimageconversionargs()
args = parser.parse_args()
if args.command is None:
    sys.exit("Please provide some arguments.")
match args.command:
    case 'convert':
        validateimageconversioncommands(args)
        convertimage(args.source, args.destination, args.format, args.compression)
    case _:
        print("Argument not recognized.")