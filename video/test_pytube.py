from pytube import YouTube
import sys
from os import path, getcwd

def progress(stream, chunk, bytes_remaining):
    percent = (100*(stream.filesize-bytes_remaining))/stream.filesize
    progress = int(percent/2)
    status = '█' * int(percent/2) + '-' * (50 - progress)
    sys.stdout.write(f' ↳ |{status}| {percent:.02f}%\r')
    sys.stdout.flush()

# basic flow but only download highest resolution for 720p
def download_normal(youtube_url, download_path=None, first=False, type='mp4'):
    connect = YouTube(youtube_url)
    stream = connect.streams.filter()
    if first:
        target = stream.first()
    else:
        target = stream.order_by('resolution').desc().first()
    if download_path:
        target.download(download_path)
    else:
        target.download()

# get stream by itag, download higher resolution videos
def download_1080(youtube_url, download_path=None, type='mp4'):
    connect = YouTube(youtube_url, on_progress_callback=progress)
    stream = connect.streams.filter(res="1080p", file_extension=type)  # mime_type="video/mp4"
    if len(stream) > 0:
        if download_path:
            stream.first().download(download_path)
        else:
            stream.first().download()
    else:
        print(f'{youtube_url} not support 1080p resolution!')
        raise ValueError

def attempt_downloads(inputs, outputdir=getcwd()):
    for i in inputs:
        if i.startswith('https'):
            print(i)
            try:
                download_1080(i, outputdir)
            except ValueError:
                download_normal(i, outputdir)
            except Exception as e:
                print(e)
                print(i)
        elif i.endswith('.txt'):
            with open(i, 'r') as rf:
                lines = rf.readlines()
            attempt_downloads(lines)

if __name__ == '__main__':
    input_arg = sys.argv[1:]
    print(input_arg)
    if path.isdir(input_arg[0]):
        attempt_downloads(input_arg[1:], outputdir=input_arg[0])
    else:
        attempt_downloads(input_arg)
