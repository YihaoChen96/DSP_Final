from scipy.io import wavfile
from mido import MidiFile
from pydub import AudioSegment
import numpy as np
import os

def loadMidi(filename):
    mid = MidiFile(filename, clip = True) # Clip values larger than 127
    return mid

def loadConfig(config_filename):
    raise NotImplementedError

def saveAudio(filename, data, sr = 44100, format = "wav", bit_depth = 16, float32 = True):

    if bit_depth == 32:
        if float32:
            dtype = np.float32
        else:
            dtype = np.int32
    elif bit_depth == 16:
        dtype = np.int16
    elif bit_depth == 8:
        dtype = np.uint8

    # Write into wav first
    wavfile.write(filename, sr, data.astype(dtype))
    
    # Convert into mp3
    if format == "mp3":
        audio = AudioSegment.from_wav(filename)
        audio.export(filename, format = "mp3")