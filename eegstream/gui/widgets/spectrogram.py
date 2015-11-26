from tkinter import *

from scipy.signal import welch

from .basic_visualizer import BasicVisualizer
from eegstream.gui.signal import SignalInterface

import numpy as np


class Spectrogram(BasicVisualizer):
    """Widget for signal visualization.

    Parameters
    ----------
    master : tkinter.Frame
        Container for widget.

    """
    def __init__(self, master, signal_interface: SignalInterface):
        self.signal_interface = signal_interface
        super().__init__(master, name='Spectrogram', interval=100,
                         data_source=signal_interface.spectrogram,
                         navigation_toolbar=True)

    def init_figure(self):
        """Function to clear figure and create empty plot."""
        # It is important, because with blit=True this function is called
        # twice.
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlim((1, 35))
        self.y_max = 0.001
        self.ax.set_ylim((0, self.y_max))
        self.line, = self.ax.plot([], [], lw=2)
        self.line.set_data([], [])
        return self.line,

    def animate_figure(self, data):
        """Function for animation process, called on each frame."""
        if data:
            x, y = data
            if self.y_max < y.max():
                self.y_max = y.max()
                self.ax.set_ylim((0, self.y_max))
                self.figure.canvas.draw()
            self.line.set_data(x, y)
        return self.line,


if __name__ == '__main__':
    root = Tk()
    widget = Spectrogram(root, data_source=iter(range(10000)))
    widget.pack(expand=TRUE, fill=BOTH)
    root.mainloop()
