from tkinter import *
from eegstream.gui.widgets.basic_visualizer import BasicVisualizer

import numpy as np


class SignalVisualizer(BasicVisualizer):
    """Widget for signal visualization.

    Parameters
    ----------
    master : tkinter.Frame
        Container for widget.

    data_source : iterable or generator
        Provides data for the animation, should return list of new values.

    """
    def __init__(self, master, data_source):
        super().__init__(master, name='Signal Visualizer', interval=25,
                         data_source=data_source)

    def init_figure(self):
        """Function to clear figure and create empty plot."""
        # It is important, because with blit=True this function is called
        # twice.
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlim((0, 2))
        self.ax.set_ylim((-2, 2))
        self.line, = self.ax.plot([], [], lw=2)
        self.line.set_data([], [])
        return self.line,

    def animate_figure(self, data):
        """Function for animation process, called on each frame."""
        #print(data)
        y = np.array(self.line.get_ydata())
        if data :
            y = np.hstack((y, np.array(data)[:, 0]))
            y = y[-250:]
            x = np.linspace(0, 2, len(y))
            self.line.set_data(x, y)
        return self.line,



if __name__ == '__main__':
    root = Tk()
    widget = SignalVisualizer(root, data_source=iter(range(10000)))
    widget.pack(expand=TRUE, fill=BOTH)
    root.mainloop()
