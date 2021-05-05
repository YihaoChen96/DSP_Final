import numpy as np
from pySynth.control.stream import Stream, MIDIStream
class AddSynth:    
    def __init__(self, *streams):
        self.streams = list(streams)
        self.max_len = max([len(s) for s in self.streams])

        for i in range(len(self.streams)):
            self.streams[i] = np.pad(self.streams[i], (0, self.max_len - len(self.streams[i])))
        self.streams = np.vstack(self.streams)
    
    def __call__(self):
        return np.sum(self.streams, axis = 0)


class WaveTable:
    def __init__(self, *streams):
        self.streams = streams
    
    def __call__(self, midi_ls):
        
        oscs = np.vstack([stream(midi_ls) for stream in self.streams])
        
        signal_stream = []
        for t in range(len(oscs[0])):
            add = AddSynth([oscs[i, t]() for i in range(len(oscs))])()
            # print(add.shape)
            signal_stream.append(add)
        signal = np.hstack(signal_stream)

        return signal