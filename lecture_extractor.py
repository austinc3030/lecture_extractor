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
from pydub import AudioSegment
from pydub.silence import split_on_silence

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


def transcribe_audio():

    filelist = glob.glob(os.path.join("extraction", '*.wav'))
    filelist.sort()

    for ii in range(0, len(filelist)):
        if ii < len(filelist)-1:
            #AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "english.wav")

            # use the audio file as the audio source
            r = sr.Recognizer()
            with sr.AudioFile("{input_filename}".format(input_filename=filelist[ii])) as source:
                audio = r.record(source) 
                
            try:
                print("Google Speech Recognition results for file {}:".format(filelist[ii]))
                print(r.recognize_google(audio))
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))



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
                  "extraction/{input_filename}_audio.wav".format(input_filename=input_filename)]
    subprocess.call(ffmpeg_cmd)

    #reading from audio mp3 file
    sound = AudioSegment.from_wav("extraction/{input_filename}_audio.wav".format(input_filename=input_filename), format="wav")
    # spliting audio files
    audio_chunks = split_on_silence(sound, min_silence_len=500, silence_thresh=-40, keep_silence=250 )
    #loop is used to iterate over the output list
    for i, chunk in enumerate(audio_chunks):
        output_file = "extracted/audio_chunk{0}.wav".format(i)
        print("Exporting file", output_file)
        chunk.export(output_file, format="wav")

    transcribe_audio()
    #shutil.rmtree("extraction")