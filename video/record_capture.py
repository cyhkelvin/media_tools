import cv2
import sys
from os import path, getcwd


class flag:
    play = True
    full_screen = False
    show_option = False
    record = True  # video
    capture = False  # image
    default_size = True
    window = True


class default:
    src = {
        'file': 'data/test.mp4',
        'rtsp': 'rtsp://root:a1s2d3f4@210.61.163.32:8889/live.sdp',
        'usbcam': '/dev/video0',
        'usb': 0
    }
    title = 'Camera'
    size = (640, 480)
    record_name = 'opencv_capture.mp4'
    max_duration = 10.0
    frame_skip = 5


def streamer(cam=cv2.VideoCapture(default.src['file']),
             max_duration=default.max_duration,
             output=getcwd(),
             name=default.record_name,
             size=default.size,
             title=default.title,
             frame_skip=default.frame_skip,
             frame_rate=None,
             capture=flag.capture,
             window=flag.window,
             record=flag.record,
             show_option=flag.show_option,
             full_screen=flag.full_screen,
             default_size=flag.default_size,
             start_time=0.0):
    frame_width = cam.get(cv2.CAP_PROP_FRAME_WIDTH)  # cam.get(3)
    frame_height = cam.get(cv2.CAP_PROP_FRAME_HEIGHT)  # cam.get(4)
    print(f'frame size:({frame_width}, {frame_height})')
    if not frame_rate:
        frame_rate = cam.get(cv2.CAP_PROP_FPS)  # cam.get(5)
    print(f'frame rate: {frame_rate}')
    FPS_MS = int((1/frame_rate)*1000)
    play = True

    if record:
        start_frame = int(start_time*frame_rate)
        max_frame = int((start_time+max_duration)*frame_rate)
        print(f'Record: {record}({max_frame} frames; {max_duration}second)')
        frame_size = (int(frame_width), int(frame_height))
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        if path.isdir(output):
            print(f'Record output: {path.join(output, name)}')
        out = cv2.VideoWriter(path.join(output, name), fourcc, frame_rate, frame_size)
    if record or capture:
        count = 0

    if window:
        if show_option:
            cv2.namedWindow(title, cv2.WINDOW_NORMAL|cv2.WINDOW_KEEPRATIO)
        else:
            cv2.namedWindow(title, cv2.WINDOW_GUI_NORMAL|cv2.WINDOW_KEEPRATIO)
        if full_screen:
            cv2.setWindowProperty(title, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        if default_size:
            cv2.resizeWindow(title, size)
        else:
            cv2.resizeWindow(title, (int(frame_width), int(frame_height)))

        ret = True
        while cv2.getWindowProperty(title, cv2.WND_PROP_VISIBLE)>=1 and ret:
            ret, img = cam.read()
            vis = img.copy()
            if record:
                if count >= max_frame:
                    record = False
                    print('record over.')
                    out.release()
                    break
                if count > start_frame:
                    out.write(vis)
            if capture and count%frame_skip==0:
                capture_path = path.join(output, f'{name}_frame{count}.png')
                if path.isdir(output):
                    print(capture_path)
                    cv2.imwrite(capture_path, vis)
                else:
                    raise(f'wrong output dir:{output}')
            if record or capture:
                count += 1
            if play:
                cv2.imshow(title, vis)
            key = cv2.waitKey(int(FPS_MS*0.7))
            if 0xFF & key == 27:  # Esc
                break
            if 0xFF & key == 13 or 0xFF & key == 32:  # Enter or Space
                play = play ^1
    else:
        ret = True
        while ret:
            ret, img = cam.read()
            vis = img.copy()
            if record:
                if count >= max_frame:
                    record = False
                    print('record over.')
                    out.release()
                    break
                if count > start_frame:
                    out.write(vis)
            if capture and count%frame_skip==0:
                capture_path = path.join(output, f'{name}_frame{count}.png')
                if path.isdir(output):
                    print(capture_path)
                    cv2.imwrite(capture_path, vis)
                else:
                    raise(f'wrong output dir:{output}')
            if record or capture:
                count += 1

    if record:
        record = False
        out.release()
    if record or capture:
        print(count)
    cam.release()
    cv2.destroyAllWindows()


def main(args):
    try:
        params = {
            'cam': None,
            'max_duration': args.duration,
            'output': args.output,
            'name': args.name,
            'size': args.size,
            'frame_skip': args.frame_skip,
            'show_option': args.show_option,
            'full_screen': args.full_screen,
            'record': args.record,
            'capture': args.capture,
            'window': args.window,
            'frame_rate': args.frame_rate,
            'start_time': args.start_time
        }
        if args.type in ['usb', 'usbcam'] and args.source.isdigit():
            params['cam'] = cv2.VideoCapture(int(args.source))
        else:
            if not args.source:
                src = default.src[args.type]
            else:
                src = args.source
            params['cam'] = cv2.VideoCapture(src)
        if args.source == path.join(args.output, args.name):
            params['record'] = False
        # streamer(cam)
        streamer(**params)
    except Exception as e:
        raise(e)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='This script support converting voc format xmls to coco format json')
    parser.add_argument('--type', type=str, default='file', help='rtsp/usb(usbcam)/file')
    parser.add_argument('--source', type=str, default=None, help='path or connected device')
    parser.add_argument('--duration', type=float, default=default.max_duration,
                        help='recording duration')
    parser.add_argument('--name', type=str, default=default.record_name, help='output file name')
    parser.add_argument('--output', type=str, default=getcwd(), help='folder path to record output files')
    parser.add_argument('--show_option', action="store_true", help='show opencv window options.')
    parser.add_argument('--full_screen', action="store_true", help='full screen.')
    parser.add_argument('--record', action="store_false", help='record audio.')
    parser.add_argument('--capture', action='store_true', help='capture frames')
    parser.add_argument('--start_time', type=float, default=0.0, help='start time of recording')
    parser.add_argument('--frame_skip', type=int, default=default.frame_skip, help='skip n-1 and capture a frame')
    parser.add_argument('--frame_rate', type=float, default=None, help='manually setting frame rate')
    parser.add_argument('--window', action="store_false", help='show window.')
    parser.add_argument('--size', help='window size.',  nargs=2, default=default.size)
    args = parser.parse_args()
    print(vars(args))
    main(args)
