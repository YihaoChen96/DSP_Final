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

    def ADSR(length,divide1=1/9,divide2=1/3.3,divide3=2/3):
        d1=int(length*divide1)
        d2=int(length*divide2)
        d3=int(length*divide3)
        result=np.zeros(length)
        for i in range(d1):
            result[i]=i/d1
        for i in range(d1,d2):
            result[i]=(-0.3*i+d2-0.7*d1)/(d2-d1)
        for i in range(d2,d3):
            result[i]=0.7
        for i in range(d3,length):
            result[i]=(-0.7*i+0.7*length)/(length-d3)
        return result
    
    def __call__(self):
        return np.mean(self.streams, axis = 0)


class WaveTable:
    def __init__(self, *streams):
        self.streams = streams
        for stream in streams:
            assert isinstance(stream, OSC) or isinstance(stream, Stream)
    
    def __call__(self):
        return np.hstack([stream() for stream in self.streams])
