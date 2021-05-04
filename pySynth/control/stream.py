import numpy as np

from pySynth.synth.effect import *
from pySynth.synth.filter import *
from pySynth.synth.oscillator import *
# from pySynth.synth.synthesizer import *

def Midi2Freq(pitch, fA4InHz = 440):
    if fA4InHz <= 0:
        return 0
    else:
        return fA4InHz * 2**((pitch-69) / 12)

class EffectChain:
    def __init__(self, *effects):
        
        self.effects = effects
        # assert isinstance(self.generator, OSC), "The first module must be an oscillator"

        
        for effect in self.effects:
            assert not isinstance(effect, OSC), "Oscillator cannot be in effect chain"

    def __call__(self, signal):


        for i in range(len(self.effects)):
            signal = self.effects[i](signal)

        return signal

class Stream:
    def __init__(self):
        pass

    def __call__(self):
        pass

class MIDIStream(Stream):
    def __init__(self, osc_type, effects_chain = None):
        self.osc_type = osc_type
        self.effects = effects_chain

    def __call__(self, midi_info_ls):
        if len(midi_info_ls) == 0:
            raise RuntimeError("Empty Midi List")

        output_stream = []

        prev_ls = [0,0,0]
        for ls in midi_info_ls: # for each note event
            [pitch, start, end] = ls
            if start - prev_ls[2] > 0: # having rest between previous event
                osc = OSC(self.osc_type,  2, start-prev_ls[2])
                # chain = Chain(osc, self.effects)
                output_stream.append(osc)
            freq = Midi2Freq(pitch)
            osc = OSC(self.osc_type , freq, end-start)
            # chain = Chain(osc, self.effects)
            output_stream.append(osc)
            prev_ls = ls

        return output_stream

    def render(self, midi_info_ls):
        if len(midi_info_ls) == 0:
            raise RuntimeError("Empty Midi List")

        output_stream = []

        prev_ls = [0,0,0]
        for ls in midi_info_ls: # for each note event
            [pitch, start, end] = ls
            if start - prev_ls[2] > 0: # having rest between previous event
                osc = OSC(self.osc_type,  2, start-prev_ls[2])
                # chain = Chain(osc, self.effects)
                output_stream.extend(osc())
            freq = Midi2Freq(pitch)
            osc = OSC(self.osc_type , freq, end-start)
            # chain = Chain(osc, self.effects)
            output_stream.extend(osc())
            prev_ls = ls

        return np.array(output_stream)