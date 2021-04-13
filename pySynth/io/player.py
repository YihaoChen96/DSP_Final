import simpleaudio as sa
import numpy as np

class Player:

    def __init__(self, sr = 44100, bit_depth = 16):
        
        self.sr = sr
        self.bit_depth = 16

    def play(self, signal, sr = None, bit_depth = None):
        
        """
            TODO: Different bit range
            TODO: Multi-channel
            Curtesy Code example from: https://realpython.com/playing-and-recording-sound-python/

            params: 
                signal: a list or numpy array containing the raw signal output
        """

        if sr is None:
            sr = self.sr
        
        if bit_depth is None:
            bit_depth = self.bit_depth


        # Ensure that highest value is in bit range
        audio = signal * (2**(bit_depth-1) - 1) / np.max(np.abs(signal))
        

        # Convert to bit_range data
        if bit_depth == 16:
            dtype = np.int16
            
        audio = audio.astype(dtype)

        # Start playback
        play_obj = sa.play_buffer(audio, 1, 2, sr)

        # Wait for playback to finish before exiting
        play_obj.wait_done()