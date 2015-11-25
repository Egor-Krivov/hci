from tkinter import *
from .basic_visualizer import BasicVisualizer

import numpy as np


class Spectrogram(BasicVisualizer):
    """Widget for signal visualization.

    Parameters
    ----------
    master : tkinter.Frame
        Container for widget.

    data_source : iterable or generator
        Provides data for the animation, should return list of new values.

    """
    def __init__(self, master, data_source):
        super().__init__(master, name='Spectrogram', interval=100,
                         data_source=data_source, navigation_toolbar=True)

    def init_figure(self):
        """Function to clear figure and create empty plot."""
        # It is important, because with blit=True this function is called
        # twice.
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlim((0, 20))
        self.ax.set_ylim((-2, 2))
        self.line, = self.ax.plot([], [], lw=2)
        self.line.set_data([], [])
        return self.line,

    def animate_figure(self, data):
        """Function for animation process, called on each frame."""
        print(data, file=sys.stderr)
        x, y = data
        print(x, y, file=sys.stderr)
        self.line.set_data(x, y)
        return self.line,



if __name__ == '__main__':
    root = Tk()
    widget = Spectrogram(root, data_source=iter(range(10000)))
    widget.pack(expand=TRUE, fill=BOTH)
    root.mainloop()
