import tkinter as tk
from collections import deque
from typing import Callable

import numpy as np

from hci.detectors import build_analyser
from hci.gui.utils import start_widget
from hci.gui.widgets.basic_visualizer import BasicVisualizer
from hci.sources import Dummy
from hci.streaming.signal_interface import WindowedSignal, MaskController


class Analyser(BasicVisualizer):
    """Widget for analysis results.

    Parameters
    ----------
    master
        Container for widget.

    windowed_signal
        Provides data for the animation, should return list of new values.

    """
    def __init__(self, master: tk.Frame, *, build_analyser: Callable=None,
                 windowed_signal: WindowedSignal,
                 mask_controller: MaskController, name='Gesture', interval=50,
                 navigation_toolbar=False):
        self.signal_interface = windowed_signal
        self.n_chans = windowed_signal.n_chans
        self.mask_controller = mask_controller
        self.build_analyser = build_analyser

        self.button = tk.Button(master, text='Activate analysis',
                                command=self.build_predictor)
        self.button.pack(side=tk.BOTTOM)

        super().__init__(master, name=name, interval=interval,
                         data_source=windowed_signal,
                         navigation_toolbar=navigation_toolbar)

        self.default_xlim = (0, self.signal_interface.window)
        self.default_ylim = (-0.2, 1.2)

        self.x = np.linspace(0, self.signal_interface.window,
                             int(windowed_signal.window / interval * 1000))

        self.predictor = None

    def build_predictor(self, name='online'):
        self.predictor = self.build_analyser(name=name)

    def init_figure(self):
        """Function to clear figure and create empty plot."""
        # It is important, because with blit=True this function is called
        # twice.
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        self.xlim = self.default_xlim
        self.ylim = self.default_ylim

        self.lines = self.ax.plot([], [], lw=2)
        self.y = deque(maxlen=len(self.x))
        return self.lines

    def animate_figure(self, data):
        """Function for animation process, called on each frame."""
        if data is not None and\
                        len(data) == self.signal_interface.epoch_len and\
                        self.predictor is not None:

            self.y.append(self.predictor(data))

            self.lines[0].set_data(self.x[:len(self.y)], self.y)
        return self.lines


if __name__ == '__main__':
    def root2widget(root):
        window = 1.0

        device = Dummy()
        mask_controller = MaskController(device.n_chans)
        stream_inlet = device.get_stream_inlet(timeout=1)
        windowed_signal = WindowedSignal(stream_inlet, window)
        widget = Analyser(root, build_analyser=build_analyser,
                          windowed_signal=windowed_signal,
                          mask_controller=mask_controller)
        return widget

    start_widget(root2widget)