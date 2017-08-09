import pyaudio
import numpy as np
from Sound.SoundAnalysis import FrequencyAnalysis

class SoundDetector:
    def __init__(self, settings):
        self.name = "SoundDetector"
        self.switchButton = False
        self.settings = settings
        self.audio = None
        self.audiostream = None
        self.freqAnalyer = FrequencyAnalysis()

    def getFreqDomain(self, bufferNum):
        data = self.audiostream.read(bufferNum)
        audio_data = np.fromstring(data, dtype=np.int16)
        audio_data = audio_data.T
        audio_data = audio_data[0:bufferNum]
        #return FrequencyAnalysis.rfft(audio_data)
        smooth_audio_data = self.freqAnalyer.windowSmoothing(audio_data, "hamming")
        return self.freqAnalyer.fftSpecturm(smooth_audio_data)

    def listen(self, win):
        N = self.settings.RATE * self.settings.TIMEWIN
        while self.switchButton:
            freqData = self.getFreqDomain(N)
            freqPower = self.freqAnalyer.fftEnergy(freqData)
            win.updateUI(freqData, freqPower)

        if self.audiostream is not None:
            self.audiostream.stop_stream()
            self.audiostream.close()
            self.audiostream = None
        if self.audio is not None:
            self.audio.terminate()
            self.audio = None


    def start(self):
        print("Sound detector starts")
        self.switchButton = True
        self.audio = pyaudio.PyAudio()
        self.audiostream = self.audio.open(format=self.settings.FORMAT, channels=self.settings.CHANNELS, rate=self.settings.RATE, input=True, frames_per_buffer=self.settings.CHUNK)

    def stop(self):
        print("Sound detector stops")
        self.switchButton = False

    def updateSettings(self, settings):
        self.settings = settings