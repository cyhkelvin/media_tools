from PIL import Image
from os import path, listdir
import argparse
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument("input_path", type=str, help="input file(png) or input dir")
parser.add_argument("-r", "--rotate", help="1 for 90; 2 for 180; 3 for 279", type=int, default=1)
args = parser.parse_args()


def rotate_and_save(file_path, rotate):
    im = Image.open(file_path)
    im_rotate = im.transpose(angle[rotate])
    im_rotate.save(path.join(path.dirname(file_path), f'output_{path.basename(file_path)}'))


input_path = args.input_path
angle = {1:Image.ROTATE_90, 2:Image.ROTATE_180, 3:Image.ROTATE_270}
if path.isfile(input_path):
    print(f'file:{input_path}')
    rotate_and_save(input_path, args.rotate)
elif path.isdir(input_path):
    print(f'dir :{input_path}')
    for file in tqdm(listdir(input_path)):
        if file.endswith('.png'):
            rotate_and_save(path.join(input_path, file), args.rotate)
else:
    raise(f'input error! {input_path}')
