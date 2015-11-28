from tkinter import *

from eegstream.gui.widgets import ControlPanel, SignalVisualizer, Spectrogram
from eegstream.streaming.signal import SignalInterface


class EEGMonitor:
    def __init__(self, signal_interface: SignalInterface):
        self.root = Tk()

        Label(self.root, text="EEGMonitor").pack()

        signal_visualizer = SignalVisualizer(self.root, signal_interface)
        signal_visualizer.pack(side=LEFT, expand=YES, fill=BOTH)

        self.right_frame = Frame(self.root)
        self.right_frame.pack(side=LEFT, expand=TRUE, fill=BOTH)
        self.control_panel = ControlPanel(self.right_frame, signal_interface)
        self.control_panel.pack(side=TOP, expand=TRUE, fill=X)

        self.spectrogram = Spectrogram(self.right_frame, signal_interface)
        self.spectrogram.pack(side=TOP, expand=TRUE, fill=BOTH)

    def start_mainloop(self):
        self.root.mainloop()


if __name__ == '__main__':
    print('Nope')
