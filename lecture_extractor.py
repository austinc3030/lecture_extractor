#!/bin/python3

import subprocess

# Filename
input_filename = "sample.wmv"

# Number of frames per second to extract from video. Note: A high sample rate here likely isn't needed for a slide show
sampling_rate = 1

if __name__ == '__main__':
    ffmpeg_cmd = ["ffmpeg",
                  "-v", "quiet", "-stats"
                  "-i", input_filename,
                  "-vf", "fps={sampling_rate}".format(sampling_rate=sampling_rate),
                  "{input_filename}_%010d.png".format(input_filename=input_filename)]
    subprocess.call(ffmpeg_cmd)