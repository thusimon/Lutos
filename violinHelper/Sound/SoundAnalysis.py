import numpy as np

class SoundAnalysis:
    def __init__(self):
        self.name = "FrequencyAnalysis"

    def windowSmoothing(self, input, windowType):
        inputLen = len(input)
        if windowType.lower() == "hamming":
            window = np.hamming(inputLen)
        elif windowType.lower() == "bartlett":
            window = np.bartlett(inputLen)
        elif windowType.lower() == "blackman":
            window = np.blackman(inputLen)
        else:
            #use hanning window by default
            window = np.hanning(inputLen)
        return input * window

    def fft(self, input):
        #real time fft
        rfftRes = np.fft.rfft(input)
        n = len(rfftRes)
        p2 = np.absolute(rfftRes/n) #two sided spectrum
        middleIdx = int(n/2+1)
        p1 = p2[0:middleIdx]
        p1[1:] = 2*p1[1:] #one sided spectrum
        return p1

    def fftEnergy(self, fftSpectrum):
        return np.sqrt(np.sum(np.absolute(fftSpectrum)**2))

    def getFreqSpectrum(self, data, windowType):
        #return FrequencyAnalysis.rfft(audio_data)
        smooth_audio_data = self.windowSmoothing(data, windowType)
        return self.fft(smooth_audio_data)