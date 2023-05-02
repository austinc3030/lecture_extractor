#!/bin/python3

import math, operator
from PIL import Image
import sys
import os
import glob
import subprocess
import shutil
import functools

# Filename
input_filename = "sample.wmv"

# Number of frames per second to extract from video. Note: A high sample rate here likely isn't needed for a slide show
sampling_rate = 1


def compare(file1, file2):
    image1 = Image.open(file1)
    image2 = Image.open(file2)
    h1 = image1.histogram()
    h2 = image2.histogram()
    rms = math.sqrt(functools.reduce(operator.add,
                                     map(lambda a,b: (a-b)**2, h1, h2))/len(h1))
    return rms


if __name__ == '__main__':
    if not os.path.exists("extraction"):
        os.mkdir("extraction")
    else:
        sys.exit("extraction already exists, exiting.")

    ffmpeg_cmd = ["ffmpeg",
                  "-v", "quiet", "-stats",
                  "-i", input_filename,
                  "-vf", "fps={sampling_rate}".format(sampling_rate=sampling_rate),
                  "extraction/{input_filename}_%010d.png".format(input_filename=input_filename)]
    subprocess.call(ffmpeg_cmd)

    filelist = glob.glob(os.path.join("extraction", '*.png'))
    filelist.sort()
    for ii in range(0, len(filelist)):
        if ii < len(filelist)-1:
            if compare(filelist[ii], filelist[ii+1]) == 0:
                print("Found similar images: {file1} and {file2}".format(file1=filelist[ii], file2=filelist[ii+1]))
            else:
                print("Found unique image: {file}".format(file=filelist[ii]))
                head, tail = os.path.split(filelist[ii])
                shutil.copyfile(filelist[ii], sys.argv[2] + os.path.sep + tail)
        else:
            shutil.copyfile(filelist[ii], sys.argv[2] + os.path.sep + tail)
    shutil.rmtree("extraction")