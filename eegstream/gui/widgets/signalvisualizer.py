from tkinter import *

import numpy as np

from eegstream.gui.widgets.basic_visualizer import BasicVisualizer
from eegstream.streaming.signal import SignalInterface


class SignalVisualizer(BasicVisualizer):
    """Widget for signal visualization.

    Parameters
    ----------
    master : tkinter.Frame
        Container for widget.

    data_source : iterable or generator
        Provides data for the animation, should return list of new values.

    """
    def __init__(self, master, signal_interface: SignalInterface):
        self.signal_interface = signal_interface
        super().__init__(master, name='Signal Visualizer', interval=25,
                         data_source=signal_interface, navigation_toolbar=True)
        self.x = np.linspace(0, signal_interface.window,
                             signal_interface.get_signal_len())

    def init_figure(self):
        """Function to clear figure and create empty plot."""
        # It is important, because with blit=True this function is called
        # twice.
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_xlim((0, self.signal_interface.window))
        ax.set_ylim((-2, 2))
        self.line, = ax.plot([], [], lw=2)
        self.line.set_data([], [])
        return self.line,

    def animate_figure(self, data):
        """Function for animation process, called on each frame."""
        if data is not None:
            self.line.set_data(self.x[:len(data[0])], data[0])
        return self.line,


if __name__ == '__main__':
    root = Tk()
    root.mainloop()
