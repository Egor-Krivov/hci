from tkinter import *

from .basic_visualizer import BasicVisualizer
from eegstream.streaming.signal import SignalInterface


class Spectrogram(BasicVisualizer):
    """Widget for signal visualization.

    Parameters
    ----------
    master : tkinter.Frame
        Container for widget.

    """
    def __init__(self, master, signal_interface: SignalInterface):
        self.signal_interface = signal_interface
        self.xlim = (1, 35)
        super().__init__(master, name='Spectrogram', interval=100,
                         data_source=signal_interface.spectrogram,
                         navigation_toolbar=True)
        self.text = StringVar(value='Val')
        Label(self, textvariable=self.text).pack(side=BOTTOM)

    def init_figure(self):
        """Function to clear figure and create empty plot."""
        # It is important, because with blit=True this function is called
        # twice.
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        self.set_default_axes()
        self.line, = self.ax.plot([], [], lw=2)
        self.line.set_data([], [])
        return self.line,

    def set_default_axes(self):
        self.y_max = 0.001
        self.ax.set_xlim(self.xlim)
        self.ax.set_ylim((0, self.y_max))

    def animate_figure(self, data):
        """Function for animation process, called on each frame."""
        if self.signal_interface.change_mask_flag:
            self.init_figure()
            self.set_default_axes()
            self.figure.canvas.draw()
            self.signal_interface.mask_changed()
        if data:
            x, y = data
            y = y[0]
            if self.y_max < y.max():
                self.y_max = y.max()
                self.ax.set_ylim((0, self.y_max))
                self.figure.canvas.draw()
            self.line.set_data(x, y)
            self.text.set(str(y.mean()))
        return self.line,



if __name__ == '__main__':
    root = Tk()
    widget = Spectrogram(root, data_source=iter(range(10000)))
    widget.pack(expand=TRUE, fill=BOTH)
    root.mainloop()
