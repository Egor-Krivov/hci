from tkinter import *

import numpy as np
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
from matplotlib.figure import Figure


class Spectrogram(Frame):
    def init(self):
        self.fig.clear()
        self.ax = ax = self.fig.add_subplot(111)
        self.ax.set_xlim((0, 2))
        self.ax.set_ylim((-2, 2))
        self.line, = ax.plot([], [], lw=2)
        self.line.set_data([], [])
        print(self.line)
        return self.line,

        # animation function.  This is called sequentially
    def animate(self, i):
        print(1)
        x = np.linspace(0, 2, 1000)
        y = np.sin(2 * np.pi * (x - 0.01 * i))
        self.line.set_data(x, y)
        return self.line,

    def __init__(self, master):
        super().__init__(master)
        master = self
        Label(master, text="Spectrogram").pack()

        # First set up the figure, the axis, and the plot element we want to animate
        self.fig = fig = Figure()


        canvas = FigureCanvasTkAgg(fig, master=master)
        toolbar = NavigationToolbar2TkAgg(canvas, master)
        toolbar.update()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=TRUE)

        # call the animator.  blit=True means only re-draw the parts that have
        # changed.
        anim = animation.FuncAnimation(fig, self.animate, init_func=self.init,
                                       interval=20, blit=True)


if __name__ == '__main__':
    root = Tk()
    widget = Spectrogram(root)
    widget.pack(expand=TRUE, fill=BOTH)
    root.mainloop()
