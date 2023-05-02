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

# Filename
input_filename = "sample.wmv"

# Number of frames per second to extract from video. Note: A high sample rate here likely isn't needed for a slide show
sampling_rate = 1


def compare(image1=None, image2=None, similarity=80):
    threshold = 1 - similarity/100
    hash_size = 8
    diff_limit = int(threshold*(hash_size**2))

    hash1 = imagehash.average_hash(image1)
    hash2 = imagehash.average_hash(image2)

    difference = hash1 - hash2

    return difference


def deduplicate(location, similarity=80):
    filelist = glob.glob(os.path.join("extraction", '*.png'))
    filelist.sort()
    count = 0
    for ii in range(0, len(filelist)):
        if ii < len(filelist)-1:
            image1 = Image.open(filelist[ii])
            image2 = Image.open(filelist[ii+1])

            difference = compare(image1, image2)
            if difference != 0:
                print("Image1: {image1} Image2: {image2} Difference: {difference}".format(image1=filelist[ii], image2=filelist[ii+1], difference=difference))
                head, tail = os.path.split(filelist[ii])
                shutil.copyfile(filelist[ii], location + os.path.sep + tail)
                count += 1
        else:
            shutil.copyfile(filelist[ii], location + os.path.sep + tail)
            count += 1
    #shutil.rmtree("extraction")

    return count


if __name__ == '__main__':

    if not os.path.exists("extraction"):
        os.mkdir("extraction")
        ffmpeg_cmd = ["ffmpeg",
                    "-v", "quiet", "-stats",
                    "-i", input_filename,
                    "-vf", "fps={sampling_rate}".format(sampling_rate=sampling_rate),
                    "extraction/{input_filename}_%010d.png".format(input_filename=input_filename)]
        subprocess.call(ffmpeg_cmd)
        
    if not os.path.exists("deduplicated"):
        os.mkdir("deduplicated")
        location = "deduplicated"
        print(deduplicate(location=location, similarity=80))