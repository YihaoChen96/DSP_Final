import math
import numpy as np
from scipy import signal

class BandPass:
    def __init__(self, Low_Band=20,High_Band=1000,number_of_degree=1):
        self.sr=44100
        self.Low=Low_Band
        self.High=High_Band
        self.Degree=number_of_degree
        
    def __call__(self, input):
        b, a = signal.butter(self.Degree, [2.0*self.Low/self.sr,2.0*self.High/self.sr], 'bandpass')
        return signal.filtfilt(b,a,input)

class LowPass:
    def __init__(self,Low_Band=20,number_of_degree=1):
        self.sr=44100
        self.Low=Low_Band
        self.Degree=number_of_degree
        
    def __call__(self, input):
        b, a = signal.butter(self.Degree, 2.0*self.Low/self.sr, 'lowpass')
        return signal.filtfilt(b,a,input)
