import simpleaudio as sa
import numpy as np

class Player:

    def __init__(self, sr = 44100):
        
        self.sr = sr
        

    def play(self, signal, sr = None):
        

        if sr is None:
            sr = self.sr

        audio = signal * (2**(16-1) - 1) / np.max(np.abs(signal))
        
        dtype = np.int16
            
        audio = audio.astype(dtype)

        # Start playback
        play_obj = sa.play_buffer(audio, 1, 2, sr)

        # Wait for playback to finish before exiting
        play_obj.wait_done()