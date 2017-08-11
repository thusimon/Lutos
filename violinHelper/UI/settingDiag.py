import tkinter as tk
from tkinter import *
from tkinter import ttk

DIAG_WIDTH = 400
DIAG_HEIGHT = 220

class SettingDiag:
    def __init__(self, settings):
        self.settings = settings
        self.top = tk.Toplevel(SettingDiag.root)
        self.frm = tk.Frame(self.top, borderwidth=4, relief='ridge')
        self.frm.pack(fill='both', expand=True)
        w = self.top.winfo_screenwidth()
        h = self.top.winfo_screenheight()
        size = (DIAG_WIDTH,DIAG_HEIGHT)
        x = w / 2 - size[0] / 2
        y = h / 2 - size[1] / 2
        self.top.focus_force()
        self.top.title("Settings")
        self.top.geometry("%dx%d+%d+%d" % (size + (x, y)))
        self.top.resizable(width=FALSE, height=FALSE)
        self.create_widgets(settings)

    def create_widgets(self, settings):
        Label(self.frm, text="Sample Rate(Hz): ").grid(row=0, column=0, padx=5, pady=10, sticky=W)
        self.rateTextVar = StringVar()
        self.rateTextVar.set(settings.RATE)
        Entry(self.frm, width=8, textvariable=self.rateTextVar).grid(row=0, column=1, padx=5, sticky=W)

        Label(self.frm, text="Time Window(ms): ").grid(row=0, column=2, padx=5)
        self.timeWinTextVar = StringVar()
        self.timeWinTextVar.set(settings.TIMEWIN)
        Entry(self.frm, width=8, textvariable=self.timeWinTextVar).grid(row=0, column=3, padx=5, sticky=W)

        Label(self.frm, text="Window Smooth: ").grid(row=1, column=0, padx=5, sticky=W)
        winType = ('hamming', 'hanning', 'bartlett', 'blackman',)
        self.winTypeCombo = ttk.Combobox(self.frm, state='readonly', value=winType, width=10)
        index = winType.index(settings.SMOOTHING)
        self.winTypeCombo.current(index)
        self.winTypeCombo.grid(row=1, column=1, padx=5, sticky=W)

        Frame(self.frm, height=2, bd=1, relief=SUNKEN).grid(row=2,column=0, columnspan=4, sticky=NSEW, padx=10, pady=15)

        Label(self.frm, text="Noise Threshold: ").grid(row=3, column=0, padx=5, sticky=W)
        self.thresholdTextVar = StringVar()
        self.thresholdTextVar.set(settings.THRESHOLD)
        Entry(self.frm, width=8, textvariable=self.thresholdTextVar).grid(row=3, column=1, padx=5, sticky=W)

        Label(self.frm, text="Freq Tolerance(Hz): ").grid(row=3, column=2, padx=5, sticky=W)
        self.toleranceTextVar = StringVar()
        self.toleranceTextVar.set(settings.TOLERANCE)
        Entry(self.frm, width=8, textvariable=self.toleranceTextVar).grid(row=3, column=3, padx=5, sticky=W)

        Label(self.frm, text="Freq Range(Hz): ").grid(row=4, column=0, padx=5, sticky=W)
        self.reqRangeTextVar = StringVar()
        self.reqRangeTextVar.set("{0},{1}".format(settings.FREQ_RANGE[0],settings.FREQ_RANGE[1]))
        Entry(self.frm, width=8, textvariable=self.reqRangeTextVar).grid(row=4, column=1, padx=5, sticky=W)

        Frame(self.frm, height=2, bd=1, relief=SUNKEN).grid(row=5, column=0, columnspan=4, sticky=NSEW, padx=10, pady=15)

        Button(self.frm, text="Save", bg="blue", fg="white", width=8, command=self.save).grid(row=6, column=1, sticky=E, padx=10)
        Button(self.frm, text="Cancel", width=8, command=self.cancel).grid(row=6, column=2, sticky=W, padx=10)

    def save(self):
        print("setting: clicked save")
        #save the settings
        self.settings.RATE = int(self.rateTextVar.get())
        self.settings.TIMEWIN = float(self.timeWinTextVar.get())
        self.settings.SMOOTHING = self.winTypeCombo.get()
        self.settings.THRESHOLD = int(self.thresholdTextVar.get())
        self.settings.TOLERANCE = int(self.toleranceTextVar.get())
        range = self.reqRangeTextVar.get().split(',')
        self.settings.FREQ_RANGE = list(map(int, range))
        self.top.destroy()
        SettingDiag.root.focus_set()

    def cancel(self):
        print("setting: clicked cancel")
        self.top.destroy()
        SettingDiag.root.focus_set()

    '''
    def entry_to_dict(self, dict_key):
        data = self.entry.get()
        if data:
            d, key = dict_key
            d[key] = data
            self.top.destroy()
    '''