import cv2
from core.lineFollower import LineFollower
from core.utils import Error

import os
import sys
import argparse
from absl import app

def main(args):
    # read image
    img = cv2.imread(args.input)

    # init line follower
    lf = LineFollower(d=1, black_text=True)

    # line thinning
    img_dst = lf.process(img)
    cv2.imwrite(args.output, img_dst)

if __name__ == '__main__':

    # Create the parser
    my_parser = argparse.ArgumentParser(description='Line Thinning by Line Following')
    my_parser.add_argument('--input', '-in', type=str,
                        help='the path of input image')
    my_parser.add_argument('--output', '-out', type=str,
                        help='the path of output image')

    # Execute and check parse_args()
    args = my_parser.parse_args()
    if args.input is None:
        Error('Path to input image is required: use --input or -i')
    if args.output is None:
        Error('Path to output image is required: use --output or -o')
    if not os.path.isfile(args.input):
        Error(f'The file specified does not exist: {args.input}')
    if os.path.isfile(args.output):
        Error(f'The file specified already exist: {args.output}')

    main(args)