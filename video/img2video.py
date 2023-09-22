import cv2
import glob
import sys
from os import path, getcwd
import argparse
import re


def main(args):
    input_dir = args.sequence
    img_type = args.image_type
    if img_type:
        img_files = glob.glob(path.join(input_dir, f'*.{img_type}'))
    else:
        for type in ['png', 'jpg']:
            img_files = glob.glob(path.join(input_dir, f'*.{type}'))
            if len(img_files) > 0:
                break
    if len(img_files) == 0:
        print('video_type only support "png" and "jpg" format!')
        return
    img_files.sort(key=lambda f: int(re.sub('\D', '', f)))
    img_array = []
    for filename in img_files:
        img = cv2.imread(filename)
        height, width, layers = img.shape
        size = (width,height)
        img_array.append(img)

    output_path = args.output
    if path.isdir(output_path):
        output_path = path.join(output_path, f'output.{args.video_type}')
        print(f'output: {output_path}')
    if args.video_type == 'mp4':
        out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), 30, size)
    elif args.video_type == 'avi':
        out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'DIVX'), 30, size)
    else:
        print('video_type only support "mp4" and "avi" format!')
        return
    
    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()

# D:\kelvin\git\MixFormer\data\lasot\person\person-1\img
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='This script convert image sequence to video.')
    parser.add_argument('--sequence', type=str, default='input/', help='input folder for image files')
    parser.add_argument('--image_type', type=str, default=None, help='type of input image format: ["jpg", "png"]')
    parser.add_argument('--video_type', type=str, default="avi", help='type of output video format: ["avi", "mp4"]')
    parser.add_argument('--output', type=str, default=getcwd(), help='folder path or file path')
    args = parser.parse_args()
    print(vars(args))
    main(args)