import numpy as np

class FrequencyAnalysis:
    def __init__(self):
        self.name = "FrequencyAnalysis"

    def rfft(input):
        return np.fft.rfft(input)

    def energy(input):
        return np.sqrt(np.sum(np.absolute(input)**2))

    def power(input):
        n = len(input)
        return FrequencyAnalysis.energy(input)/n