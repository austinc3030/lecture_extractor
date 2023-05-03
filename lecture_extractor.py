#!/bin/python3

import math, operator
from PIL import Image
import sys
import os
import glob
import subprocess
import shutil
import functools
import imagehash
import numpy as np
import ffmpeg

# Filename
input_filename = "sample.wmv"

# Number of frames per second to extract from video. Note: A high sample rate here likely isn't needed for a slide show
sampling_rate = 1

# Threshold: The number of bits that are allowed to differ between image hashes for determining similarity.
# A value of 5 seem to be effective to prevent duplicate slides due to cursor movements. Can adjust as needed
threshold = 5

# Number of seconds to chunk the audio into. Google speech to text only accepts 60 seconds at a time
audio_chunk_seconds = 30


def compare(image1=None, image2=None, similarity=80):
    threshold = 1 - similarity/100
    hash_size = 8
    diff_limit = int(threshold*(hash_size**2))

    hash1 = imagehash.average_hash(image1)
    hash2 = imagehash.average_hash(image2)

    difference = hash1 - hash2

    return difference


def deduplicate(location, threshold=5):
    filelist = glob.glob(os.path.join("extraction", '*.png'))
    filelist.sort()
    count = 0
    for ii in range(0, len(filelist)):
        if ii < len(filelist)-1:
            image1 = Image.open(filelist[ii])
            image2 = Image.open(filelist[ii+1])

            difference = compare(image1, image2)
            if difference > 5:
                head, tail = os.path.split(filelist[ii])
                shutil.copyfile(filelist[ii], location + os.path.sep + tail)
                count += 1
        else:
            shutil.copyfile(filelist[ii], location + os.path.sep + tail)
            count += 1

    return count


def new_frame_dict(frame_index=0, frame_timestamp=0, frame_filename=""):
    
    return {"frame_index": frame_index,
            "frame_timestamp": frame_timestamp,
            "frame_filename": frame_filename} 


if __name__ == '__main__':

    # TODO: Do not rely on dirs existing to determine whether to do something. Eventually implement in argparse
    if not os.path.exists("extracted"):
        os.mkdir("extracted")

        filename="sample.wmv"
        probe = ffmpeg.probe(filename)
        duration_exact = float(probe['streams'][0]['duration'])
        duration_whole_second = int(duration_exact)

        frames = []

        for i in range(0, duration_whole_second):
            output_filename = "extracted/{filename}_{index}.png".format(filename=filename, index=i)
            ffmpeg.input(filename, ss=i).output(output_filename, vframes=1, loglevel="quiet").run()
            frames.append(new_frame_dict(frame_index=i, frame_timestamp=i, frame_filename=output_filename))

        print(frames)

    # #shutil.rmtree("extraction")