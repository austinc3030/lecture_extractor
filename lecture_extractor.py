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

    # DEFAULTS
    INPUT_FILENAME = "sample.wmv"
    TEMP_DIR = "./temp"
    EXTRACT_DIR = TEMP_DIR + "extract"
    SAMPLING_RATE = 1
    DEDUP_DIR = TEMP_DIR + "dedup"
    THRESHOLD = 5


    def __init__(self, input_filename=None, temp_dir=None, extract_dir=None, sampling_rate=None,
                 dedup_dir=None, threshold=None):

        # Set defaults
        self.input_filename = self.INPUT_FILENAME
        self.temp_dir = self.TEMP_DIR
        self.extract_dir = self.EXTRACT_DIR
        self.sampling_rate = self.SAMPLING_RATE
        self.dedup_dir = self.DEDUP_DIR
        self.threshold = self.THRESHOLD

        if input_filename is not None:
            self.input_filename = input_filename

        if temp_dir is not None:
            self.temp_dir = temp_dir

        if extract_dir is not None:
            self.extract_dir = extract_dir

        if sampling_rate is not None:
            self.sampling_rate = sampling_rate
    
        if dedup_dir is not None:
            self.dedup_dir = dedup_dir

        if threshold is not None:
            self.threshold = threshold
            


    def deduplicate_frames(self, threshold=5):
        if not os.path.exists(self.dedup_dir):
            os.mkdir(self.dedup_dir)
            filelist = glob.glob(os.path.join(self.extract_dir, '*.png'))
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
                        shutil.copyfile(filelist[ii], self.dedup_dir + os.path.sep + tail)
                        count += 1
                else:
                    shutil.copyfile(filelist[ii], self.dedup_dir + os.path.sep + tail)
                    count += 1
            
            progress_bar.close()
        
            print("Found {number_of_slides} slide(s)".format(number_of_slides=count))


    def extract_frames(self):
        if not os.path.exists(self.extract_dir):
            os.mkdir(self.extract_dir)
            ffmpeg_cmd = ["ffmpeg",
                        "-v", "quiet", "-stats",
                        "-i", self.input_filename,
                        "-vf", "fps={sampling_rate}".format(sampling_rate=self.sampling_rate),
                        "{extract_dir}/{input_filename}_%010d.png".format(extract_dir=self.extract_dir,
                                                                          input_filename=self.input_filename)]
            subprocess.call(ffmpeg_cmd)


    def main(self):
        self.extract_frames()
        self.deduplicate_frames()


if __name__ == '__main__':
    lecture_extractor = LectureExtractor()
    lecture_extractor.main()
    sys.exit(0)  # Assume exit successfully