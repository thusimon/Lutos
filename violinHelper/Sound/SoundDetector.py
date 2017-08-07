import pyaudio
import numpy as np
from Sound.SoundAnalysis import FrequencyAnalysis

CHUNK = 2048 # The size of the chunk to read from the mic stream
FORMAT = pyaudio.paInt16 # The format depends on the mic used
CHANNELS = 1 # The number of channels used to record the audio. Depends on the mic
RATE = 44100 # The sample rate for audio. Depends on the mic
START = 0

FREQ_RANGE = [140, 900]


class SoundDetector:
    switchButton = False

    def __init__(self):
        self.name = "SoundDetector"
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

    def listen(self, timewin, win):
        N = RATE * timewin
        while self.switchButton:
            freqData = self.getFreqDomain(N)
            freqPower = self.freqAnalyer.fftEnergy(freqData)
            '''
            powerMsg = "noise" if (freqPower < THRESHOLD) else str(freqPower)
            clen = len(freqData)
            cminIdx = 0 if (clen < FREQ_RANGE[0]) else FREQ_RANGE[0]
            cmaxIdx = FREQ_RANGE[1] if (clen > FREQ_RANGE[1]) else clen
            freqDataTrim = freqData[cminIdx:cmaxIdx]
            maxFreq = np.argmax(freqDataTrim) + cminIdx
            print("Power = " + powerMsg + ", maxFreq = " + str(maxFreq))
            '''
            win.updateUI(freqData, freqPower)


    def start(self):
        print("Sound detector starts")
        self.switchButton = True
        self.audio = pyaudio.PyAudio()
        self.audiostream = self.audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    def stop(self):
        print("Sound detector stops")
        self.switchButton = False
        if self.audiostream is not None:
            self.audiostream.stop_stream()
            self.audiostream.close()
            self.audiostream = None
        if self.audio is not None:
            self.audio.terminate()
            self.audio = None

'''
if __name__ == "__main__":
    mySound = SoundDetector()
    mySound.start();
    mySound.listen(1, None)
'''