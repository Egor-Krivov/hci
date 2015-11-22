from tkinter import *
from widgets import ControlPanel, SignalVisualizer, Spectrogram


class EEGMonitor(Frame):
    def __init__(self, master):
        super().__init__(master)
        master = self
        Label(master, text="EEGMonitor").pack()

        SignalVisualizer(master).pack(side=LEFT)

        self.right_frame = Frame(master)
        self.right_frame.pack(side=LEFT)
        self.control_panel = ControlPanel(self.right_frame, background='red')
        self.control_panel.pack(side=TOP, expand=TRUE, fill=BOTH)

        self.spectrogram = Spectrogram(self.right_frame)
        self.spectrogram.pack(side=TOP)



#        self.right_frame.focus_set()


if __name__ == '__main__':
    root = Tk()
    widget = EEGMonitor(root)
    widget.pack(expand=TRUE, fill=BOTH)
    root.mainloop()
