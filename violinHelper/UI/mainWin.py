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
        self.soundDetectModule = None
        self.bgthread = None
        master.title("Audio Frequency analysis")
        master.geometry('%dx%d+%d+%d' % (1200, 800, 100, 100))

        self.customFont = tkFont.Font(family="Helvetica", size=40)
        panel1 = PanedWindow(master=master, orient=VERTICAL,relief='groove')
        panel1.place(x=800, y=10)
        label1 = Label(panel1, text="E", font=self.customFont).grid(row=0,column=0)
        self.textvar1 = StringVar()
        self.textvar1.set("")
        self.text1 = Entry(panel1, width=10, font=self.customFont, textvariable=self.textvar1)
        self.text1.grid(row=0,column=1)

        label2 = Label(panel1, text="Hz", font=self.customFont).grid(row=1, column=0)
        self.textvar2 = StringVar()
        self.textvar2.set("")
        self.text2 = Entry(panel1, width=10, font=self.customFont, textvariable=self.textvar2)
        self.text2.grid(row=1, column=1)

        label3 = Label(panel1, text="Nt", font=self.customFont).grid(row=2, column=0)
        self.textvar3 = StringVar()
        self.textvar3.set("")
        self.text3 = Entry(panel1, width=10, font=self.customFont, textvariable=self.textvar3)
        self.text3.grid(row=2, column=1)

        label5 = Label(panel1, text="SF", font=self.customFont).grid(row=3, column=0)
        self.textvar5 = StringVar()
        self.textvar5.set("")
        self.text5 = Entry(panel1, width=10, font=self.customFont, textvariable=self.textvar5)
        self.text5.grid(row=3, column=1)

        panel2 = PanedWindow(master=master, orient=HORIZONTAL, relief='groove')
        panel2.place(x=800, y=600)
        btn1 = Button(panel2, text="Start", command=self.startBtnCallBack, font=self.customFont).grid(row=0, column=0, padx=(0,20))
        btn2 = Button(panel2, text="Stop", command=self.stopBtnCallBack, font=self.customFont).grid(row=0, column=1, padx=(20,0))

        panel3 = PanedWindow(master=master, orient=HORIZONTAL, width=600)
        panel3.place(x=0, y=10)
        label4 = Label(panel3, text="Frequency Domain", font=tkFont.Font(family="Helvetica", size=18)).grid(row=0, column=0)
        self.fig = Figure(figsize=(8, 8), dpi=100)

        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.show()
        self.canvas.get_tk_widget().grid(row=1,column=0, pady=40, sticky="nesw")
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel('Hz', alpha=0.5)
        self.ax.set_ylabel('Magnitude', alpha=0.5)

        self.notes = FreqTable()

    def startBtnCallBack(self):
        print("Start!")
        self.soundDetectModule = SoundDetector()
        self.soundDetectModule.start()
        self.bgthread = threading.Thread(target=self.processAudio)
        self.bgthread.start()

    def stopBtnCallBack(self):
        print("Stop!")
        if self.bgthread is not None:
            self.bgthread.join()
        if self.soundDetectModule is not None:
            self.soundDetectModule.stop()
            self.soundDetectModule = None

    def processAudio(self):
        if self.soundDetectModule is not None:
            self.soundDetectModule.listen(TimeWindow, self)

    def updateUI(self, freqData, freqPower):
        updateFlag = False if (freqPower < THRESHOLD) else True
        powerMsg = "No Detection" if not updateFlag else str(freqPower)
        clen = len(freqData)
        cminIdx = 0 if (clen < FREQ_RANGE[0]) else FREQ_RANGE[0]
        cmaxIdx = FREQ_RANGE[1] if (clen > FREQ_RANGE[1]) else clen
        freqDataTrim = freqData[cminIdx:cmaxIdx]
        maxFreq = np.argmax(freqDataTrim) + cminIdx
        freqMsg = "No Detection" if not updateFlag else str(maxFreq)
        print("UI: Power = " + powerMsg + ", maxFreq = " + str(maxFreq))
        self.textvar1.set(powerMsg)
        self.textvar2.set(freqMsg)
        self.updateCanvas(range(cminIdx,cmaxIdx),freqDataTrim)
        self.updateNotes(updateFlag, maxFreq)

    def updateCanvas(self, freqX, freqY):
        self.ax.cla()
        self.ax.plot(freqX, freqY)
        self.canvas.draw()

    def updateNotes(self,updateFlag, maxFreq):
        if not updateFlag:
            self.textvar3.set("No Detection")
            self.textvar5.set("No Detection")
            self.text3.configure(bg="white")
        else:
            for key, value in self.notes.freqTable.items():
                if abs(value-maxFreq) <= TOLERANCE:
                    #found the note
                    self.textvar5.set(str(value))
                    self.textvar3.set(str(key))
                    if maxFreq > value:
                        self.text3.configure(bg="red")
                    else:
                        self.text3.configure(bg="green")
                    return
            self.textvar3.set("No Detection")
            self.textvar5.set("No Detection")
            self.text3.configure(bg="white")


if __name__ == '__main__':
    root = Tk()
    my_gui = mainWin(root)
    root.mainloop()