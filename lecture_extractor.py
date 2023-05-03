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


class LectureExtractor(object):

    input_filename = "sample.wmv"
    
    # Number of frames per second to extract from video. Note: A high sample rate here likely isn't needed for a
    # slide show
    sampling_rate = 1
    
    # Threshold: The number of bits that are allowed to differ between image hashes for determining similarity.
    # A value of 5 seem to be effective to prevent duplicate slides due to cursor movements. Can adjust as needed
    threshold = 5


    def __init__(self):
        self.input_filename = "sample.wmv"
        self.sampling_rate = 1
        self.threshold = 5


    def compare(self, image1=None, image2=None, similarity=80):
        threshold = 1 - similarity/100
        hash_size = 8
        diff_limit = int(threshold*(hash_size**2))

        hash1 = imagehash.average_hash(image1)
        hash2 = imagehash.average_hash(image2)

        difference = hash1 - hash2

        return difference


    def deduplicate(self, location, threshold=5):
        filelist = glob.glob(os.path.join("extraction", '*.png'))
        filelist.sort()
        count = 0
        for ii in range(0, len(filelist)):
            if ii < len(filelist)-1:
                image1 = Image.open(filelist[ii])
                image2 = Image.open(filelist[ii+1])

                difference = self.compare(image1, image2)
                if difference > 5:
                    head, tail = os.path.split(filelist[ii])
                    shutil.copyfile(filelist[ii], location + os.path.sep + tail)
                    count += 1
            else:
                shutil.copyfile(filelist[ii], location + os.path.sep + tail)
                count += 1

        return count


    def main(self):
        # TODO: Do not rely on dirs existing to determine whether to do something. Eventually implement in argparse
        if not os.path.exists("extracted"):
            os.mkdir("extracted")

            filename="sample.wmv"
            probe = ffmpeg.probe(filename)
            duration_exact = float(probe['streams'][0]['duration'])
            duration_whole_second = int(duration_exact)

            for i in range(0, duration_whole_second):
                output_filename = "extracted/{filename}_{index}.png".format(filename=filename, index=i)
                ffmpeg.input(filename, ss=i).output(output_filename, vframes=1, loglevel="quiet").run()

        #shutil.rmtree("extraction")


if __name__ == '__main__':
    lecture_extractor = LectureExtractor()
    lecture_extractor.main()
    sys.exit(0)  # Assume exit successfully