#!/bin/python3

import ffmpeg

# Filename
input_filename = "sample.wmv"

# Number of frames per second to extract from video. Note: A high sample rate here likely isn't needed for a slide show
video_sampling_rate = 1

if __name__ == '__main__':
    stream = ffmpeg.input(input_filename)
    stream = ffmpeg.filter(stream, 'fps', fps=1)
    stream = ffmpeg.filter_multi_output("{input_filename}_%010d.png".format(input_filename=input_filename))
    ffmpeg.run(steam)