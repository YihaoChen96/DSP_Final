import numpy as np

from .oscillator import OSC
from .filter import BandPass, LowPass
from .effect import Chorus
from pySynth.control.stream import Stream, MIDIStream
class AddSynth:
    def __init__(self, *streams):
        self.streams = streams
        for stream in streams:
            assert isinstance(stream, OSC) or isinstance(stream, Stream)
    
    def __call__(self):
        return np.mean([stream() for stream in self.streams], axis = 0)


class WaveTable:
    def __init__(self, *streams):
        self.streams = streams
        for stream in streams:
            assert isinstance(stream, OSC) or isinstance(stream, Stream)
    
    def __call__(self):
        return np.hstack([stream() for stream in self.streams])