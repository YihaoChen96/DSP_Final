import os
from glob import glob

import pretty_midi
import numpy as np
from scipy.io import wavfile
import soundfile as sf

pretty_midi.pretty_midi.MAX_TICK = 1e10

class ReadMIDI(object):
    '''
    read midi file into a list of [pitch, start, end]
    assume midi file only have 1 track
    '''
    def __init__(self, midi_filepath):
        self.midi_fp = midi_filepath
        self.midi_info_ls = []

    def __call__(self):
        midi_data = pretty_midi.PrettyMIDI(self.midi_fp)
        for instrument in midi_data.instruments:
            notes = instrument.notes
            for note in notes:
                start = note.start
                end = note.end
                pitch = note.pitch
                velocity = note.velocity
                self.midi_info_ls.append([pitch, start, end])
        return self.midi_info_ls
        #outputs.sort(key=lambda elem: elem[0])

def saveAudio(filename, data, sr = 44100, format = "wav", bit_depth = 16):

    if bit_depth == 16:
        dtype = "PCM_16"
    elif bit_depth == 24:
        dtype = "PCM_24"
    elif bit_depth == 8:
        dtype = "PCM_S8"
    else:
        raise Exception("Bit depth not supported")

    # Write into wav first
    # wavfile.write(filename, sr, data.astype(dtype))
    
    sf.write(filename, data, sr, subtype=dtype, format = format)


    # # Convert into mp3
    # if format == "mp3":
    #     audio = AudioSegment.from_wav(filename)
    #     audio.export(filename, format = "mp3")

'''
# test script
d = os.getcwd()
midi_fp = "midi/test.mid"
midi_filepath = os.path.join(d, midi_fp)

midi_func = ReadMIDI(midi_filepath)
midi_ls = midi_func()
print(midi_ls)

# >>> [[60, 0.0, 0.5], [64, 0.5, 1.0], [67, 1.0, 1.5], [64, 2.0, 2.5], [62, 2.5, 2.75], 
# [60, 2.75, 3.0], [62, 3.0, 3.125], [60, 3.25, 3.375], [60, 3.5, 4.0], [69, 4.0, 4.5], 
# [67, 4.5, 5.0], [62, 5.0, 5.25], [64, 5.25, 5.5], [62, 5.5, 5.75], [62, 5.75, 6.0], 
# [64, 6.0, 6.25], [60, 6.5, 7.0], [62, 7.0, 7.5], [60, 7.5, 8.0]]
'''

