#Adjust image resolution

# Checklist 
# The user can specify target width and height 
# The output image matches the requested resolution. 
# Error messages are displayed for invalid dimension.

import sys
import argparse
import pathlib
import cv2
import utilities


MAX_DIMENSION = 4096



def add_resize_arguments(subparsers, parent):
    """Add arguments for the resize command."""
    resize_parser = subparsers.add_parser('resize', help='Resize an image to specified dimensions', parents=[parent])
    resize_parser.add_argument('-s', '--source', type=utilities.valid_file, required=True, help='Source image')
    resize_parser.add_argument('-d', '--destination', help='Destination image.')
    resize_parser.add_argument('--width', type=int, required=True, help='Target width of the output image')
    resize_parser.add_argument('--height', type=int, required=True, help='Target height of the output image')
    
def validate_resize_arguments(args):
    """Validate the resize arguments."""
    if args.width <= 0 or args.height <= 0:
        utilities.error("Width and height must be positive integers.")
    if args.width > MAX_DIMENSION or args.height > MAX_DIMENSION:
        utilities.error(f"Width and height must not exceed {MAX_DIMENSION}.")
    
    # validate source path
    args.source = utilities.normalize_source(args.source)
    utilities.validate_supported_format(args.source, "source")

    # destination
    args.destination = utilities.prepare_destination(args.destination, args.source, "_resized" + args.source.suffix)
    utilities.validate_supported_format(args.destination, "destination")

def resize_image(args):
    """Resize the image to the specified dimensions."""
    img = cv2.imread(str(args.source))
    if img is None:
        utilities.error(f"Failed to read the source image: {args.source}")
    
    # choose interpolation: area for shrinking, linear for enlarging
    h, w = img.shape[:2]
    if args.width < w and args.height < h:
        interp = cv2.INTER_AREA
    else:
        interp = cv2.INTER_LINEAR
    
    resized_img = cv2.resize(img, (args.width, args.height), interpolation=interp)
    
    # ensure the destination path is unique if it already exists. If --force is not specified, we will generate a unique path.
    realdest = utilities.givecorrectdestination(args.destination, args.force)
    
    ok = cv2.imwrite(str(realdest), resized_img)
    if not ok:
        utilities.error(f"Failed to write the output image: {realdest}")
    
    print(f"\033[32mImage resized successfully: {realdest} ({args.width}x{args.height}\033[0m)")
