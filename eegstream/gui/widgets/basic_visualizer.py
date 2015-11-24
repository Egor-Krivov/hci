from tkinter import *

import numpy as np
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
from matplotlib.figure import Figure


class BasicVisualizer(Frame):
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
    def __init__(self, master, name='Basic Visualizer', interval=25,
                 data_source=iter(range(10**5)), navigation_toolbar=False):
        # This provides consistency for widget/frame system. Now object can
        # be used as frame, can be packed.
        super().__init__(master)

        # Now this Frame is a container for all the rest
        master = self

        Label(master, text=name).pack()

        self.figure = Figure()
        canvas = FigureCanvasTkAgg(self.figure, master=master)
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=TRUE)

        # It is for navigation buttons
        if navigation_toolbar:
            toolbar = NavigationToolbar2TkAgg(canvas, master)
            toolbar.update()

        # call the animator.  blit=True means only re-draw the parts that have
        # changed.
        animation.FuncAnimation(self.figure, interval=interval, blit=True,
                                func=self.animate_figure,
                                frames=data_source,
                                init_func=self.init_figure)

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
        x = np.linspace(0, 2, 1000)
        y = np.sin(2 * np.pi * (x + 0.01 * data))
        self.line.set_data(x, y)
        return self.line,


if __name__ == '__main__':
    root = Tk()
    widget = BasicVisualizer(root)
    widget.pack(expand=TRUE, fill=BOTH)
    root.mainloop()
