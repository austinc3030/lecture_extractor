#!/bin/python3

import ffmpeg

filename="sample.wmv"
probe = ffmpeg.probe(filename)
duration_exact = float(probe['streams'][0]['duration'])
duration_whole_second = int(duration_exact)

for i in range(0, duration_whole_second):
    ffmpeg.input(filename, ss=i).output('filename_' + str(i) + '.png', vframes=1).run()