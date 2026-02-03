import sys
import cv2
args = sys.argv[1:]
argLength = len(args)
if argLength < 1:
    print("Please provide some arguments.")
    sys.exit()
img = cv2.imread(args[0]) #Hardcode for now
cv2.imwrite(args[1],img,[cv2.IMWRITE_JPEG2000_COMPRESSION_X1000, 3])
