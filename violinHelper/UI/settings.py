import pyaudio

class AudioSettings:
    def __init__(self):
        self.CHUNK = 2048 # The size of the chunk to read from the mic stream
        self.FORMAT = pyaudio.paInt16  # The format depends on the mic used
        self.CHANNELS = 1 # The number of channels used to record the audio. Depends on the mic
        self.RATE = 44100 # The sample rate for audio. Depends on the mic
        self.TIMEWIN = 1 # seconds, the time domain window to process the audio signal, can be treated as the refresh speed
        self.SMOOTHING = "hamming" # the window smoothing method, hamming by default

class DisplaySettings:
    def __init__(self):
        self.THRESHOLD = 400 # if the spectrum power in the AudioSettings.TIMEWIN is less than threshold, consider as noise
        self.TOLERANCE = 5 # the spectrum peak's freq is x, find the pitch between [x-5, x+5]
        self.FREQ_RANGE = [140, 900]  # the frequency range to display the spectrum