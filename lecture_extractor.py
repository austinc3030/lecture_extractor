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
import speech_recognition as sr

# Filename
input_filename = "sample.wmv"

# Number of frames per second to extract from video. Note: A high sample rate here likely isn't needed for a slide show
sampling_rate = 1

# Threshold: The number of bits that are allowed to differ between image hashes for determining similarity.
# A value of 5 seem to be effective to prevent duplicate slides due to cursor movements. Can adjust as needed
threshold = 5


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
    shutil.rmtree("extraction")

    return count


if __name__ == '__main__':

    # TODO: Do not rely on dirs existing to determine whether to do something. Eventually implement in argparse
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
        number_of_slides = deduplicate(location=location, threshold=threshold)

        print("Found {number_of_slides} slide(s)".format(number_of_slides=number_of_slides))

    ffmpeg_cmd = ["ffmpeg",
                  "-v", "quiet", "-stats",
                  "-i", input_filename,
                  "{input_filename}_audio.wav".format(input_filename=input_filename)]
    subprocess.call(ffmpeg_cmd)
    
    #AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "english.wav")
    AUDIO_FILE = "{input_filename}_audio.wav".format(input_filename=input_filename)

    # use the audio file as the audio source
    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source) 
        
    try:
        print("Google Speech Recognition results:")
        print(r.recognize_google(audio, show_all=True))
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))