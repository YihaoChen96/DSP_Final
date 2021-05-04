import numpy as np
from pySynth.synth.oscillator import OSC
import math
from scipy import signal
from scipy.signal import convolve
from scipy.io.wavfile import write
from IPython.display import Audio
import soundfile as sf
import copy
import sys
import wave
import os
import struct

class RingBuffer(object):
    def __init__(self, maxDelay):
        self.maxDelay = maxDelay + 1
        self.buf = np.zeros(self.maxDelay)
        self.writeInd = 0

    def pushSample(self, s):
        self.buf[self.writeInd] = s
        self.writeInd = (self.writeInd + 1) % len(self.buf)

    def delayedSample(self, d):
        d = min(self.maxDelay - 1, max(0, d))
        i = ((self.writeInd + self.maxDelay) - d) % self.maxDelay
        return self.buf[i]
    
class LinearWrap(object):
    def __init__(self, it):
        self.it = it
        
    def __len__(self):
        return len(self.it)
        
    def __setitem__(self, inI, val):
        if type(inI) != int:
            raise RuntimeError('Can only write to integer values')
        self.it[inI] = val

    def __getitem__(self, inI):
        loI = math.floor(inI)
        hiI = math.ceil(inI)
        a = inI - loI
        inRange = lambda val: val >= 0 and val < len(self.it)
        loX = self.it[loI] if inRange(loI) else 0
        hiX = self.it[hiI] if inRange(hiI) else 0
        return loX * (1-a) + hiX * a
    
    
class LinearRingBuffer(RingBuffer):
    def __init__(self, maxDelay):
        self.maxDelay = maxDelay + 1
        self.buf = LinearWrap(np.zeros(self.maxDelay))
        self.writeInd = 0


class Vibrato(object):
    def __init__(self, maxDelaySamps = 100, feedback = -0.7):
        '''
        Effect1 - vibrato with feedback
        Inputs: 
        - maxDelaySamps
        - feedback
        '''   
        self.mds = maxDelaySamps
        self.FB = feedback
        self.sr = 44100

    def __call__(self, signal):
        signal = LinearWrap(signal)
        outputSamps = len(signal) + self.mds
        output = np.zeros(outputSamps)
        ringBuf = LinearRingBuffer(self.mds)
        prevDelaySamp = 0

        fmod = 1
        deltaPhi = fmod/self.sr
        phi = 0
        for i in range(outputSamps):
            s = signal[i] if i < len(signal) else 0 
            s += prevDelaySamp * self.FB
            ringBuf.pushSample(s)
            delaySamps = int((math.sin(2 * math.pi * phi) + 1.001) * self.mds)
            prevDelaySamp = ringBuf.delayedSample(delaySamps)
            output[i] = ringBuf.delayedSample(delaySamps) * 0.5

            phi = phi + deltaPhi
            while phi >= 1:
                phi -= 1
        return output
    

class Chorus(object):
    def __init__(self, fmod = 1.5, BL=1.0, FF=0.7):
        '''
        Effect2 - Chorus
        Inputs: 
        - fmod (modulation frequency in Hertz)
        - BL 
        - FF
        '''
        self.fmod = fmod
        self.BL = BL
        self.FF = FF
        self.sr = 44100

    def __call__(self, signal):  
        signal = LinearWrap(signal)
        A = int(0.002 * self.sr) # Modulation amplitude in samples
        M = int(0.002 * self.sr) # Static delay in samples
        if A > M:
            raise RuntimeError("Amplitude of vibrato too high for delay length")

        maxDelaySamps = M + A + 2 
        outputSamps = len(signal) + maxDelaySamps
        output = np.zeros(outputSamps)
        ringBuf = LinearRingBuffer(maxDelaySamps)
        deltaPhi = self.fmod/self.sr
        phi = 0

        for i in range(outputSamps):
            s = signal[i]
            ringBuf.pushSample(s)
            delaySamps = M + int(math.sin(2 * math.pi * phi) * A)
            output[i] = s * self.BL + ringBuf.delayedSample(delaySamps) * self.FF

            phi = phi + deltaPhi
            while phi >= 1:
                phi -= 1
        return output
    

class Wahwah(object):
    def __init__(self, min_cutoff=300, max_cutoff=4000, rate=10000, damp=0.2):
        '''
        Effect2 - Wahwah
        Inputs: 
        - min_cutoff
        - max_cutoff
        - rate
        - damp
        ''' 
        self.min_cutoff = min_cutoff
        self.max_cutoff = max_cutoff
        self.rate = rate
        self.damp = damp
        self.sr = 44100

    def __call__(self, signal): 
        signal = LinearWrap(signal)
        center_freq = self.rate/self.sr
        cutoff_freq = np.arange(self.min_cutoff , self.max_cutoff, center_freq).tolist()
        while len(cutoff_freq) < len(signal):
            min_max_idx = np.arange(self.max_cutoff ,  self.min_cutoff, -center_freq).tolist()
            max_min_idx = np.arange(self.min_cutoff ,  self.max_cutoff, center_freq).tolist()
            cutoff_freq.extend(min_max_idx)
            cutoff_freq.extend(max_min_idx)

        
        cutoff_freq = np.asarray(cutoff_freq)[0:len(signal)]
        F1 = 2 * math.sin((math.pi*cutoff_freq[0]/self.sr))
        Q1 = 2 * self.damp
        
        highpass=np.zeros(len(signal))
        bandpass=np.zeros(len(signal))
        lowpass=np.zeros(len(signal))
                     
        highpass[0] = signal[0]
        bandpass[0] = F1*highpass[0]
        lowpass[0] = F1*bandpass[0]
                     
        for n in range(1, len(signal)):
            highpass[n] = signal[n] - lowpass[n-1] - Q1*bandpass[n-1]
            bandpass[n] = F1*highpass[n] + bandpass[n-1]
            lowpass[n] = F1*bandpass[n] + lowpass[n-1]
            F1 = 2*math.sin((math.pi*cutoff_freq[n])/self.sr)
        
        #normalize
        normed = bandpass/max(abs(bandpass))
        return bandpass


class Reverb(object):
    def __init__(self, gain_dry = 1, gain_wet = 1, reverb_type = "hall"):
        '''
        Convolutional Reverb
        Inputs: 
        - gain_dry
        - gain_wet
        - reverb_type: 'room', 'hall', 'parking_garage'
        '''
        self.gain_dry = gain_dry
        self.gain_wet = gain_wet
        self.reverb_type = reverb_type
        self.sr = 44100
    
    def get_reverb_in(self):
        # load reverb impulse samples, downloaded from https://www.voxengo.com/impulses/
        if self.reverb_type == "room":
            fp = 'IMreverbs/Nice Drum Room.wav'
        elif self.reverb_type == "hall":
            fp = 'IMreverbs/Large Long Echo Hall.wav'
        elif self.reverb_type == "parking_garage":
            fp = 'IMreverbs/Parking Garage.wav'
        else:
            raise ValueError("Unknown Reverb Type.")
        
        cur_dir = os.path.dirname(__file__)
        type_path = os.path.join(cur_dir, fp)
        wav_file = wave.open(type_path, 'r')
        num_samples_reverb = wav_file.getnframes()
        num_channels_reverb = wav_file.getnchannels()
        reverb = wav_file.readframes(num_samples_reverb)
        total_samples_reverb = num_samples_reverb * num_channels_reverb
        wav_file.close()
        
        reverb = struct.unpack('{n}h'.format(n = total_samples_reverb), reverb)
        reverb = np.array([reverb[0::2], reverb[1::2]], dtype = np.float64)
        reverb[0] /= np.max(np.abs(reverb[0]), axis = 0)
        # print(reverb[0])
        return reverb[0]
            

    def __call__(self, signal):  

        num_samples_signal = len(signal)
        
        reverb = self.get_reverb_in()
        
        output = np.zeros(2*num_samples_signal - 1, dtype = np.float64)
        output = (convolve(signal * self.gain_dry, reverb * self.gain_wet, method = 'fft'))
    
        return output



class Delay(object):
    def __init__(self, delayTime = 0.25):
        '''
        Add on effect - Delay
        input: delayTime
        '''
        self.dt = delayTime
        self.sr = 44100
    
    def __call__(self, signal):
        delaySamps = int(self.dt * self.sr)
        outputSamps = len(signal) + delaySamps

        output = np.zeros(outputSamps)
        ringBuf = RingBuffer(delaySamps)
        for i in range(outputSamps):
            s = signal[i] if i < len(signal) else 0
            ringBuf.pushSample(s)
            output[i] = s * 0.5 + ringBuf.delayedSample(delaySamps) * 0.5
        return output



