import math
import numpy as np

import os
import sys


class ADSR:
    def __init__(self, divide1=1/9, divide2=2/9, divide3=5/9):
        
        assert divide1 >0 and divide2 > 0 and divide3 >0, "Division points must be greater than 0"
        assert divide1 <=divide2<=divide3 <=1, "Division points must all be less or equal to 1 in ascending order"

        # division_sum = np.sum([divide1, divide2, divide3])
        self.divide1 = divide1
        self.divide2 = divide2
        self.divide3 = divide3

    def __call__(self, length):

        d1=int(length*self.divide1)
        d2=int(length*self.divide2)
        d3=int(length*self.divide3)
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


class OSC:
    """ Base Class for Oscillators """

    def __init__(self, name, freq = None, length = None, adsr = None):

        """ 
            Specify argument for initialization.
            Example usage:
                osc = OSC("sine", 440)
                osc() # Call this function will generate 
            params:
                xxx: ...
                xxx: ...
            
            output:
                xxx: ...
            
            TODO: For each function, specify params and output in docstring
        
        """
        
        self.name=name
        assert self.name in ["sine", "triangle", "square"], "Osc only support sine, triangle, and square wave"
        
        self.freq=freq
        self.length=length
        self.adsr = adsr
        
        

    def __call__(self, freq = None, length = None, adsr = None):#The default audio sample rate is 44100
        
        assert self.freq is not None or freq is not None, "OSC needs non-None value for frequency when is initialized or called"
        assert self.length is not None or length is not None, "OSC needs non-None value for length when is initialized or called"

        if freq is None:
            freq = self.freq
        
        if length is None:
            length = self.length

        if adsr is None:
            adsr = self.adsr
        
        sampleRate=44100
        """ Define behavior each time this instance is called """
        sample_num = int(sampleRate * length)

        result=np.zeros(sample_num)
        if self.name=='sine':
            rate = freq/sampleRate
            for i in range(sample_num):
                result[i]=math.sin(2*math.pi*(i*rate))
        if self.name=='triangle':
            rate = freq/sampleRate
            for i in range(sample_num):
                pecent=(i%(1/rate))*rate
                if pecent<=0.25:
                    result[i]=4*pecent
                if pecent>0.25 and pecent<=0.75:
                    result[i]=-4*(pecent)+2
                if pecent>0.75:
                    result[i]=4*pecent-4
        if self.name=='square':
            rate= freq/sampleRate
            for i in range(sample_num):
                pecent=(i%(1/rate))*rate
                if pecent==0:
                    result[i]=0
                if pecent<0.5 and pecent!=0:
                    result[i]=1
                if pecent>0.5 and pecent!=0:
                    result[i]=-1
                if pecent==0.5:
                    result[i]=0
        if adsr is not None:
            result = result * adsr(sample_num)
        return result


class GenerateFromMIDI(object):
    '''
    generate oscillator array from midi file
    input: midi_info_ls (from io/IO.py), contains lists of [pitch, start, end]
    output: oscillator array 
    '''
    def __init__(self, midi_info_list, osc_type):
        self.midi_info_ls =  midi_info_list
        self.osc_type = osc_type
        self.output_osc_array = []


    def ToolMidi2Freq(self, pitch, fA4InHz = 440):
        if fA4InHz <= 0:
            return 0
        else:
            return fA4InHz * 2**((pitch-69) / 12)
    
    def __call__(self):
        if len(self.midi_info_ls) == 0:
            raise RuntimeError("Empty Midi List")

        prev_ls = [0,0,0]
        for ls in self.midi_info_ls: # for each note event
            [pitch, start, end] = ls
            if start - prev_ls[2] > 0: # having rest between previous event
                osc = OSC(self.osc_type,  2, start-prev_ls[2])
                self.output_osc_array.extend(osc())
            freq = self.ToolMidi2Freq(pitch)
            osc = OSC(self.osc_type , freq, end-start)
            self.output_osc_array.extend(osc())
            prev_ls = ls
        #norm = np.linalg.norm(self.output_osc_array)
        #self.output_osc_array = self.output_osc_array/norm
        return self.output_osc_array





'''
midi_ls = [[60, 0.0, 0.5], [64, 0.5, 1.0], [67, 1.0, 1.5], [64, 2.0, 2.5], [62, 2.5, 2.75], [60, 2.75, 3.0], [62, 3.0, 3.125], [60, 3.25, 3.375], [60, 3.5, 4.0], [69, 4.0, 4.5], [67, 4.5, 5.0], [62, 5.0, 5.25], [64, 5.25, 5.5], [62, 5.5, 5.75], [62, 5.75, 6.0], [64, 6.0, 6.25], [60, 6.5, 7.0], [62, 7.0, 7.5], [60, 7.5, 8.0]]
osc_arr = GenerateFromMIDI(midi_ls, "sine")
osc_array = osc_arr() # the audio array 
'''
 