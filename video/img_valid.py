import cv2
import numpy as np


# comparison 2 methods
# https://blog.csdn.net/weixin_42954710/article/details/119063995
def detect_blur_fft(img, size=150, thres=10):
    # method 1: detect blur with FFT
    # https://pyimagesearch.com/2015/09/07/blur-detection-with-opencv/
    h, w = img.shape[:2]
    cx, cy = int(w/2.0), int(h/2.0)
    fft = np.fft.fft2(img)
    fftshift = np.fft.fftshift(fft)
    fftshift[cy-size:cy+size, cx-size:cx+size] = 0
    fftshift = np.fft.ifftshift(fftshift)
    recon = np.fft.ifft2(fftshift)
    magnitude = 20*np.log(np.abs(recon))
    mean = np.mean(magnitude)
    return mean, mean <= thres

def detect_blur_laplacian(img, thres=50):
    # method 2 detect blur with Laplace distribution and empirical threshold
    # https://blog.csdn.net/qq_34784753/article/details/72901616
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    value = cv2.Laplacian(img, cv2.CV_64F).var()
    value_gray = cv2.Laplacian(gray, cv2.CV_64F).var()
    print(value, value_gray, thres)
    return value <= thres



if __name__ == '__main__':
    import os, sys
    from shutil import copy
    img_paths = os.listdir(sys.argv[1])
    img_paths = [os.path.join(sys.argv[1], fpath) for fpath in img_paths]
    # img_paths = ['./test_clear.png', './test_blur.png']
    for img_path in img_paths:
        if not img_path.endswith('.png'):
            continue
        try:
            image = cv2.imread(img_path)

            fft_args = {'size':int(min(image.shape[:2])/3), 'thres':21}
            mean, is_blur = detect_blur_fft(image, **fft_args)
            # print(img_path, fft_args['thres'], mean)
            if is_blur:
                print(f'[fft] image {img_path} is blurred. thres:({fft_args["thres"]}), mean({mean})')
                copy(img_path, os.getcwd())
            else:
                print(f'[fft] image {img_path} is clear. thres:({fft_args["thres"]}), mean({mean})')

            laplace_thres = 50
            if detect_blur_laplacian(image, thres=laplace_thres):
                print(f'[laplace] image {img_path} is blurred. thres:({laplace_thres})')
                # copy(img_path, os.getcwd())
            else:
                print(f'[laplace] image {img_path} is clear. thres:({laplace_thres})')
        except Exception as e:
            print(e)
            break

    
    