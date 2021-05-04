import numpy as np

from .oscillator import OSC
from .filter import BandPass, LowPass
from .effect import Chorus
from pySynth.control.stream import Stream, MIDIStream
class AddSynth:    
    def __init__(self, *streams):
        self.streams = list(streams)
        self.max_len = max([len(s) for s in self.streams])

        for i in range(len(self.streams)):
            self.streams[i] = np.pad(self.streams[i], (0, self.max_len - len(self.streams[i])))

    
    def __call__(self):
        return np.mean(self.streams, axis = 0)


class WaveTable:
    def __init__(self, *streams):
        self.streams = streams
    
    def __call__(self, midi_ls):
        
        oscs = np.vstack([stream(midi_ls) for stream in self.streams])
        
        signal_stream = []
        for t in range(len(oscs[0])):
            add = AddSynth([oscs[i, t]() for i in range(len(oscs))])()
            signal_stream.append(add)
        return np.hstack(signal_stream)