import numpy as np

class Buffer:
    def __init__(self, settings):
        self.chunkSize = settings.CHUNK
        self.rate = settings.RATE
        self.bufferSize = settings.RATE * settings.BUFF_TIMEWIN
        self.format = settings.FORMAT
        #TODO other dtypes
        self.data = np.array([], np.int16)

    def pushToBuffer(self, newData):
        self.data = np.append(self.data, newData)
        self.data = self.data[-self.bufferSize:]