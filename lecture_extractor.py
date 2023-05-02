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

def compare_1(image1=None, image2=None):
    h1 = image1.histogram()
    h2 = image2.histogram()
    rms = math.sqrt(functools.reduce(operator.add,
                                     map(lambda a,b: (a-b)**2, h1, h2))/len(h1))
    return rms


def compare_2(image1=None, image2=None, similarity=80):
    threshold = 1 - similarity/100
    hash_size = 8
    diff_limit = int(threshold*(hash_size**2))

    hash1 = imagehash.average_hash(image1, hash_size).hash
    hash2 = imagehash.average_hash(image2, hash_size).hash

    if np.count_nonzero(hash1 != hash2) <= diff_limit:
        return 0
    else:
        return 1


def deduplicate(location, similarity=80, method=1):
    filelist = glob.glob(os.path.join("extraction", '*.png'))
    filelist.sort()
    for ii in range(0, len(filelist)):
        if ii < len(filelist)-1:
            image1 = Image.open(filelist[ii])
            image2 = Image.open(filelist[ii+1])

            if method == 1:
                unique = compare_1(image1, image2)
            elif method == 2:
                unique = compare_2(image1, image2)
            else:
                unique = compare_1(image1, image2)

            if unique == 0:
                print("Found similar images: {file1} and {file2}".format(file1=filelist[ii], file2=filelist[ii+1]))
            else:
                print("Found unique image: {file}".format(file=filelist[ii]))
                head, tail = os.path.split(filelist[ii])
                shutil.copyfile(filelist[ii], location + os.path.sep + tail)
        else:
            shutil.copyfile(filelist[ii], location + os.path.sep + tail)
    #shutil.rmtree("extraction")


if __name__ == '__main__':
    if not os.path.exists("extraction"):
        os.mkdir("extraction")
    else:
        sys.exit("extraction already exists, exiting.")
    
    if not os.path.exists("deduplicated1"):
        os.mkdir("deduplicated1")
    else:
        sys.exit("deduplicated1 already exists, exiting.")

    if not os.path.exists("deduplicated2"):
        os.mkdir("deduplicated2")
    else:
        sys.exit("deduplicated2 already exists, exiting.")

    ffmpeg_cmd = ["ffmpeg",
                  "-v", "quiet", "-stats",
                  "-i", input_filename,
                  "-vf", "fps={sampling_rate}".format(sampling_rate=sampling_rate),
                  "extraction/{input_filename}_%010d.png".format(input_filename=input_filename)]
    subprocess.call(ffmpeg_cmd)

    #location1 = "deduplicated1"
    location2 = "deduplicated2"
    #deduplicate(location=location1, similarity=80, method=1)
    deduplicate(location=location2, similarity=50, method=2)