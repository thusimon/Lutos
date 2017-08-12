import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter.font as tkFont
import threading
from Sound.SoundDetector import *
from Sound.SoundAnalysis import *
from Sound.FreqTable import *
from UI.settings import *
from UI.settingDiag import *

MAINWIN_WIDTH = 1200
MAINWIN_HEIGHT = 700

class mainWin:
    def __init__(self, master):
        self.master = master
        self.Setting = Settings()
        self.soundDetectModule = SoundDetector(self.Setting)
        self.soundAnalysisModule = SoundAnalysis()
        self.importAudioDataThread = None
        self.updateUIThread = None
        self.pitches = FreqTable()
        self.noDetect = "--"
        master.title("Audio Frequency analysis")
        w = master .winfo_screenwidth()
        h = master .winfo_screenheight()
        size = (MAINWIN_WIDTH, MAINWIN_HEIGHT)
        x = w / 2 - size[0] / 2
        y = h / 2 - size[1] / 2
        master.geometry("%dx%d+%d+%d" % (size + (x, y)))
        master.resizable(width=FALSE, height=FALSE)
        self.master.protocol("WM_DELETE_WINDOW", self.exitBtnCallBack)
        SettingDiag.root = self.master
        self.create_widgets()

    def create_widgets(self):
        self.customFont = tkFont.Font(family="Helvetica", size=20)

        #add menu
        menubar = Menu(self.master)
        actionMenu = Menu(menubar, tearoff=0)
        actionMenu.add_command(label="Start", command=self.startBtnCallBack)
        actionMenu.add_command(label="Stop", command=self.stopBtnCallBack)
        actionMenu.add_separator()
        actionMenu.add_command(label="Exit", command=self.exitBtnCallBack)
        menubar.add_cascade(label="Action", menu=actionMenu)

        settingMenu = Menu(menubar, tearoff=0)
        settingMenu.add_command(label="Settings", command=self.settingBtnCallBack)
        menubar.add_cascade(label="Preference", menu=settingMenu)

        self.master.config(menu=menubar)

        # audio statistics display
        pane1 = PanedWindow(master=self.master)
        pane1.grid(row=0, column=0, sticky=NSEW)
        Label(pane1, text="Volume:", font=self.customFont).grid(row=0,column=0)
        self.volumeTextVar = StringVar()
        self.volumeTextVar.set("")
        self.volumeTextEntry = Entry(pane1, width=8, font=self.customFont, textvariable=self.volumeTextVar)
        self.volumeTextEntry.grid(row=0, column=1)
        Label(pane1, text="Freq Peak:", font=self.customFont).grid(row=0, column=2,padx=10)
        self.freqTextVar = StringVar()
        self.freqTextVar.set("")
        self.freqTextEntry = Entry(pane1, width=8, font=self.customFont, textvariable=self.freqTextVar)
        self.freqTextEntry.grid(row=0, column=3)
        Label(pane1, text="Pitch Name:", font=self.customFont).grid(row=0, column=4,padx=10)
        self.pitchNTextVar = StringVar()
        self.pitchNTextVar.set("")
        self.pitchNTextEntry = Entry(pane1, width=8, font=self.customFont, textvariable=self.pitchNTextVar)
        self.pitchNTextEntry.grid(row=0, column=5)
        Label(pane1, text="Pitch Freq:", font=self.customFont).grid(row=0, column=6,padx=10)
        self.pitchFTextVar = StringVar()
        self.pitchFTextVar.set("")
        self.pitchFTextEntry = Entry(pane1, width=10, font=self.customFont, textvariable=self.pitchFTextVar)
        self.pitchFTextEntry.grid(row=0, column=7)

        # audio spectrum display
        pane2 = PanedWindow(master=self.master)
        pane2.grid(row=1, column=0, sticky=NSEW)
        self.fig = Figure(figsize=(14, 8), dpi=80, facecolor='w', edgecolor='k')
        self.fig.text(0.5,0.9,"Audio Spectrum")
        self.canvas = FigureCanvasTkAgg(self.fig, master=pane2)
        self.canvas.get_tk_widget().grid(row=0,column=0, sticky=NSEW)
        self.ax = self.fig.add_subplot(111)
        self.resetCanvas()
        self.canvas.show()

    def startBtnCallBack(self):
        if self.soundDetectModule.switchButton:
            print("already started, please stop first")
            return

        print("Start!")
        self.soundDetectModule.start()
        self.importAudioDataThread = threading.Thread(target=self.soundDetectModule.importAudioData)
        self.importAudioDataThread.start()
        self.updateUI()

    def stopBtnCallBack(self):
        print("Stop!")
        self.soundDetectModule.stop()
        self.resetCanvas()
        if self.updateUIThread is not None:
            self.updateUIThread.cancel()

        if self.importAudioDataThread is not None:
            self.importAudioDataThread.join(timeout=1.0)
            print("bgthread terminates")

    def exitBtnCallBack(self):
        print("exit")
        self.stopBtnCallBack()
        self.master.quit()

    def settingBtnCallBack(self):
        print("settings")
        print(self.Setting.TOLERANCE)
        SettingDiag(self.Setting)

    def updateUI(self):
        if not self.soundDetectModule.switchButton:
            print("stopped, no update")
            return

        self.updateUIThread = threading.Timer(self.Setting.TIMEWIN / 1000, self.updateUI)
        self.updateUIThread.start()

        audioBuffer = self.soundDetectModule.buffer.data
        audioData = audioBuffer[-self.Setting.PROCESS_DATALEN:]
        if len(audioData)<self.Setting.CHUNK:
            print("not enough data, return and wait for the next call")
            return

        freqData = self.soundAnalysisModule.getFreqSpectrum(audioData, self.Setting.SMOOTHING)
        freqPower = self.soundAnalysisModule.fftEnergy(freqData)
        updateFlag = False if (freqPower < self.Setting.THRESHOLD) else True
        powerMsg = self.noDetect if not updateFlag else str(freqPower)
        clen = len(freqData)
        cminIdx = 0 if (clen < self.Setting.FREQ_RANGE[0]) else self.Setting.FREQ_RANGE[0]
        cmaxIdx = self.Setting.FREQ_RANGE[1] if (clen > self.Setting.FREQ_RANGE[1]) else clen
        freqDataTrim = freqData[cminIdx:cmaxIdx]
        maxFreq = np.argmax(freqDataTrim) + cminIdx
        freqMsg = self.noDetect if not updateFlag else str(maxFreq)
        print("UI: Power = " + powerMsg + ", maxFreq = " + str(maxFreq))
        self.volumeTextVar.set(powerMsg)
        self.freqTextVar.set(freqMsg)
        self.updateCanvas(range(cminIdx,cmaxIdx),freqDataTrim)
        self.updateNotes(updateFlag, maxFreq)


    def updateCanvas(self, freqX, freqY):
        self.ax.cla()
        self.ax.plot(freqX, freqY)
        self.ax.set_xlabel('Hz', alpha=0.5)
        self.ax.set_ylabel('Magnitude', alpha=0.5)
        self.canvas.draw()

    def resetCanvas(self):
        self.ax.cla()
        self.ax.set_xlabel('Hz', alpha=0.5)
        self.ax.set_xbound(lower=0, upper=1)
        self.ax.set_ylabel('Magnitude', alpha=0.5)
        self.ax.set_ybound(lower=0, upper=1)
        self.canvas.draw()

    def updateNotes(self,updateFlag, maxFreq):
        if not updateFlag:
            self.pitchNTextVar.set(self.noDetect)
            self.pitchFTextVar.set(self.noDetect)
            self.pitchNTextEntry.configure(bg="white")
        else:
            for key, value in self.pitches.freqTable.items():
                if abs(value-maxFreq) <= self.Setting.TOLERANCE:
                    #found the note
                    self.pitchFTextVar.set(str(value))
                    self.pitchNTextVar.set(str(key))
                    if maxFreq > value:
                        self.pitchNTextEntry.configure(bg="red")
                    else:
                        self.pitchNTextEntry.configure(bg="green")
                    return
            self.pitchNTextVar.set(self.noDetect)
            self.pitchFTextVar.set(self.noDetect)
            self.pitchNTextEntry.configure(bg="white")


if __name__ == '__main__':
    root = Tk()
    my_gui = mainWin(root)
    root.mainloop()