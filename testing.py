#!/bin/python3

import ffmpeg

filename="sample.wmv"
probe = ffmpeg.probe(filename)
time = float(probe['streams'][0]['duration'])
print(time)