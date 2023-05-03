#!/bin/python3

import imagehash
import glob
import os
import shutil
import subprocess
import sys

from PIL import Image
from tqdm import tqdm


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


    def deduplicate_frames(self, threshold=5):
        if not os.path.exists("deduplicated"):
            os.mkdir("deduplicated")
            filelist = glob.glob(os.path.join("extraction", '*.png'))
            filelist.sort()
            count = 0
            progress_bar = tqdm(range(0, len(filelist)))
            progress_bar.set_description("Finding Slides")
            for ii in progress_bar:
                if ii < len(filelist)-1:
                    image1 = Image.open(filelist[ii])
                    image2 = Image.open(filelist[ii+1])
                    hash1 = imagehash.average_hash(image1)
                    hash2 = imagehash.average_hash(image2)

                    difference = hash1 - hash2

                    # **********************************************************
                    # TODO: Need logic here to index the found slides, including
                    # first and last appearances, as well as duration
                    # **********************************************************

                    if difference > 5:
                        head, tail = os.path.split(filelist[ii])
                        shutil.copyfile(filelist[ii], "extraction" + os.path.sep + tail)
                        count += 1
                else:
                    shutil.copyfile(filelist[ii], "extraction" + os.path.sep + tail)
                    count += 1
            
            progress_bar.close()
            shutil.rmtree("extraction")
        
            print("Found {number_of_slides} slide(s)".format(number_of_slides=count))


    def extract_frames(self):
        if not os.path.exists("extraction"):
            os.mkdir("extraction")
            ffmpeg_cmd = ["ffmpeg",
                        "-v", "quiet", "-stats",
                        "-i", self.input_filename,
                        "-vf", "fps={sampling_rate}".format(sampling_rate=self.sampling_rate),
                        "extraction/{input_filename}_%010d.png".format(input_filename=self.input_filename)]
            subprocess.call(ffmpeg_cmd)


    def main(self):
        self.extract_frames()
        self.deduplicate_frames()


if __name__ == '__main__':
    lecture_extractor = LectureExtractor()
    lecture_extractor.main()
    sys.exit(0)  # Assume exit successfully