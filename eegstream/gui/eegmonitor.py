from tkinter import *
from eegstream.gui.widgets import ControlPanel, SignalVisualizer, Spectrogram


class EEGMonitor:
    def __init__(self, signal_source, spectrogram_source):
        self.root = Tk()
        Label(self.root, text="EEGMonitor").pack()

        SignalVisualizer(self.root, signal_source).pack(side=LEFT)

        self.right_frame = Frame(self.root)
        self.right_frame.pack(side=LEFT, expand=TRUE, fill=BOTH)
        self.control_panel = ControlPanel(self.right_frame)
        self.control_panel.pack(side=TOP, expand=TRUE, fill=BOTH)

        self.spectrogram = Spectrogram(self.right_frame, spectrogram_source)
        self.spectrogram.pack(side=TOP, expand=TRUE, fill=BOTH)

    def start_mainloop(self):
        self.root.mainloop()


if __name__ == '__main__':
    eegmonitor = EEGMonitor(iter(range(10000)), iter(range(10000)))
    eegmonitor.start_mainloop()
