import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from tkinter import *
import tkinter.font as tkFont
import threading
from Sound.SoundDetector import *
from Sound.FreqTable import *

TimeWindow = 1
THRESHOLD = 400 # The threshold intensity that defines silence.
TOLERANCE = 5

class mainWin:

    def __init__(self, master):
        self.master = master
        self.soundDetectModule = SoundDetector()
        self.bgthread = None
        self.pitches = FreqTable()
        self.noDetect = "--"
        master.title("Audio Frequency analysis")
        master.geometry('%dx%d+%d+%d' % (1200, 700, 100, 100))
        master.resizable(width=FALSE, height=FALSE)
        self.master.protocol("WM_DELETE_WINDOW", self.exitBtnCallBack)
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
        settingMenu.add_command(label="Audio", command=self.audioSettingBtnCallBack)
        settingMenu.add_command(label="Display", command=self.displaySettingBtnCallBack)
        menubar.add_cascade(label="Settings", menu=settingMenu)

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
        self.canvas.show()
        self.canvas.get_tk_widget().grid(row=0,column=0, sticky=NSEW)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel('Hz', alpha=0.5)
        self.ax.set_ylabel('Magnitude', alpha=0.5)

    def startBtnCallBack(self):
        if self.soundDetectModule.switchButton:
            print("already started, please stop first")
            return

        print("Start!")
        self.soundDetectModule.start()
        self.bgthread = threading.Thread(target=self.soundDetectModule.listen, args = (TimeWindow,self))
        self.bgthread.start()

    def stopBtnCallBack(self):
        print("Stop!")
        self.soundDetectModule.stop()
        if self.bgthread is not None:
            self.bgthread.join(timeout=1.0)
            print("bgthread terminates")

    def exitBtnCallBack(self):
        print("exit")
        self.stopBtnCallBack()
        self.master.quit()

    def audioSettingBtnCallBack(self):
        print("audio setting")

    def displaySettingBtnCallBack(self):
        print("display setting")

    def processAudio(self):
        self.soundDetectModule.listen(TimeWindow, self)

    def updateUI(self, freqData, freqPower):
        if not self.soundDetectModule.switchButton:
            print("stopped, no update")
            return

        updateFlag = False if (freqPower < THRESHOLD) else True
        powerMsg = self.noDetect if not updateFlag else str(freqPower)
        clen = len(freqData)
        cminIdx = 0 if (clen < FREQ_RANGE[0]) else FREQ_RANGE[0]
        cmaxIdx = FREQ_RANGE[1] if (clen > FREQ_RANGE[1]) else clen
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
        self.canvas.draw()

    def updateNotes(self,updateFlag, maxFreq):
        if not updateFlag:
            self.pitchNTextVar.set(self.noDetect)
            self.pitchFTextVar.set(self.noDetect)
            self.pitchNTextEntry.configure(bg="white")
        else:
            for key, value in self.pitches.freqTable.items():
                if abs(value-maxFreq) <= TOLERANCE:
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