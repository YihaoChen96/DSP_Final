import math
import numpy as np

class OSC:
    """ Base Class for Oscillators """

    def __init__(self,name,freq, length):

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
        self.Name=name
        self.Freq=freq
        self.length=length
        
        

    def __call__(self):#The default audio sample rate is 44100
        sampleRate=44100
        """ Define behavior each time this instance is called """
        result=np.zeros(sampleRate*self.length)
        if self.Name=='sine':
            rate=self.Freq/sampleRate
            for i in range(sampleRate*self.length):
                result[i]=math.sin(2*math.pi*(i*rate))
        if self.Name=='triangle':
            rate=self.Freq/sampleRate
            for i in range(sampleRate*self.length):
                pecent=(i%(1/rate))*rate
                if pecent<=0.25:
                    result[i]=4*pecent
                if pecent>0.25 and pecent<=0.75:
                    result[i]=-4*(pecent)+2
                if pecent>0.75:
                    result[i]=4*pecent-4
        if self.Name=='square':
            rate=self.Freq/sampleRate
            for i in range(sampleRate*self.length):
                pecent=(i%(1/rate))*rate
                if pecent==0:
                    result[i]=0
                if pecent<0.5 and pecent!=0:
                    result[i]=1
                if pecent>0.5 and pecent!=0:
                    result[i]=-1
                if pecent==0.5:
                    result[i]=0
        return result