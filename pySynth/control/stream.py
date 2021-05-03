from pySynth.synth.effect import *
from pySynth.synth.filter import *
from pySynth.synth.oscillator import *
from pySynth.synth.synthesizer import *


class Chain:
    def __init__(self, module_list):

        self.module_list = module_list

    def generate(self):

        assert isinstance(self.module_list[0], OSC), "The first module must be an oscillator"

        for i in module_list:
            assert not isinstance(self.module_list[i], OSC), "Oscillator must be the first module"

        signal = module_list[0]()
        for i in range(1, len(module_list)):
            signal = module_list[i](signal)

        return signal

class Stream:
    def __init__(self, input, chain):
        pass

    def __call__(self):
        pass