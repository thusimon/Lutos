import pyaudio
import numpy as np
from Sound.Buffer import Buffer

class SoundDetector:
    def __init__(self, settings):
        self.name = "SoundDetector"
        self.switchButton = False
        self.settings = settings
        self.buffer = Buffer(self.settings)
        self.audio = None
        self.audiostream = None

    def importAudioData(self):
        N = self.settings.CHUNK* self.settings.BUFF_TIMEWIN
        while self.switchButton:
            data = self.audiostream.read(N)
            audio_data = np.fromstring(data, dtype=np.int16)
            audio_data = audio_data.T
            audio_data = audio_data[0:N]
            self.buffer.pushToBuffer(audio_data)

        if self.audiostream is not None:
            self.audiostream.stop_stream()
            self.audiostream.close()
            self.audiostream = None
        if self.audio is not None:
            self.audio.terminate()
            self.audio = None


    def start(self):
        print("Sound detector starts")
        self.audio = pyaudio.PyAudio()
        self.audiostream = self.audio.open(format=self.settings.FORMAT, channels=self.settings.CHANNELS, rate=self.settings.RATE, input=True, frames_per_buffer=self.settings.CHUNK)
        self.buffer = Buffer(self.settings)
        self.switchButton = True

    def stop(self):
        print("Sound detector stops")
        self.switchButton = False