import tkinter as tk

import matplotlib.animation as animation
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
from matplotlib.figure import Figure

from hci.gui.utils import start_widget


class BasicVisualizer(tk.Frame):
    """ Basic visualizer. It is a tkinter widget that is used to visualize data
    To use it, user should change *** methods. It is inherited from Frame to be
    packed and used just as any other widget.

    Parameters
    ----------
    master : Frame
        Container for visualizer.

    name : str
        Name of visualizer. It is written above figure.

    interval: int
        Interval between frames of animation in milliseconds.

    data_source : iterable or generator
        Provides data for the animation.

    navigation_toolbar : boolean
        Whether to plot navigation bar below the figure.

    """
    def __init__(self, master: tk.Frame, name='Basic Visualizer', interval=25,
                 data_source=iter(range(10**5)), navigation_toolbar=False):
        # This provides consistency for widget/frame system. Now object can
        # be used as frame, can be packed.
        super().__init__(master)

        self.label = tk.Label(self, text=name)
        self.label.pack(side=tk.TOP)

        self.figure = Figure()
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # It is for navigation buttons
        if navigation_toolbar:
            self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
            self.toolbar.update()

        self.default_xlim = (0, 2)
        self.default_ylim = (-2, 2)

        # call the animator. blit=True means only re-draw the parts that have
        # changed.
        self.animation = animation.FuncAnimation(
            self.figure, interval=interval, blit=False,
            func=self.animate_figure, frames=data_source,
            init_func=self.init_figure)

    @property
    def xlim(self):
        return self._xlim

    @xlim.setter
    def xlim(self, limits):
        self._xlim = limits
        self.ax.set_xlim(limits)

    @property
    def ylim(self):
        return self._ylim

    @ylim.setter
    def ylim(self, limits):
        self._ylim = limits
        self.ax.set_ylim(limits)

    def init_figure(self):
        """Function to clear figure and create empty plot."""
        # It is important, because with blit=True this function is called
        # twice.
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        self.xlim = self.default_xlim
        self.ylim = self.default_ylim
        self.line, = self.ax.plot([], [], lw=2)
        self.line.set_data([], [])
        return self.line,

    def animate_figure(self, data):
        """Function for animation process, called on each frame."""
        x = np.linspace(0, 2, 1000)
        y = np.sin(2 * np.pi * (x + 0.01 * data))
        self.line.set_data(x, y)
        return self.line,


if __name__ == '__main__':
    start_widget(lambda root: BasicVisualizer(root, navigation_toolbar=True))