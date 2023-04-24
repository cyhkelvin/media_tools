
# ffmpeg
 - rotate
    `ffmpeg -i INPUT.mov -vf "transpose=1" OUTPUT.mov [1:90度; 3:270度]`
    `ffmpeg -i input.mp4 -filter:v "transpose=1,transpose=1 [180度]`
 - trim
    `ffmpeg -i input.mp4 -ss 00:05:20 -t 00:10:00 -c:v copy -c:a copy output1.mp4`
    `ffmpeg -i input.mp4 -ss 00:05:10 -to 00:15:30 -c:v copy -c:a copy output2.mp4`
