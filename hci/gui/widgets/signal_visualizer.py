import tkinter as tk

import numpy as np

from hci.gui.utils import start_widget
from hci.gui.widgets.basic_visualizer import BasicVisualizer
from hci.sources import Dummy
from hci.streaming.signal_interface import WindowedSignal, MaskController


class SignalVisualizer(BasicVisualizer):
    """Widget for signal visualization.

    Parameters
    ----------
    master
        Container for widget.

    windowed_signal
        Windowed signal class for the animation, should return list of new values.

    """
    def __init__(self, master: tk.Frame, windowed_signal: WindowedSignal,
                 mask_controller: MaskController, name='Signal Visualizer',
                 interval=75, navigation_toolbar=False):
        self.windowed_signal = windowed_signal
        self.n_chans = windowed_signal.n_chans
        self.mask_controller = mask_controller

        super().__init__(master, name=name, interval=interval,
                         data_source=windowed_signal,
                         navigation_toolbar=navigation_toolbar)

        self.default_xlim = (0, self.windowed_signal.window)
        self.default_ylim = (-2, 2)

        self.x = np.linspace(0, self.windowed_signal.window,
                             self.windowed_signal.epoch_len)
        self.y = None

    def init_figure(self):
        """Function to clear figure and create empty plot."""
        # It is important, because with blit=True this function is called
        # twice.
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        self.xlim = self.default_xlim
        self.ylim = self.default_ylim

        data = [[]]*self.mask_controller.n_chans*2
        self.lines = self.ax.plot(*data, lw=0)

        return self.lines

    def animate_figure(self, y):
        """Function for animation process, called on each frame."""
        if y is not None and len(y) > 0:
            self.y = y

            mask = self.mask_controller.mask
            for i, line in enumerate(self.lines):
                line.set_linewidth(1 if mask[i] else 0)
                line.set_data(self.x[:len(y)], y[:, i])

            self.auto_ylim(force=True)
        return self.lines

    def auto_ylim(self, force=False):
        mask = self.mask_controller.mask
        if self.y is not None and np.any(mask):
            max_value = np.max(self.y[:, mask])
            min_value = np.min(self.y[:, mask])
            new_lim = list(self.ylim)
            if force or max_value > self.ylim[1]:
                new_lim[1] = max_value
            if force or min_value < self.ylim[0]:
                new_lim[0] = min_value
            self.ylim = new_lim


if __name__ == '__main__':
    def root2widget(root):
        window = 1.0

        device = Dummy()
        mask_controller = MaskController(device.n_chans)
        stream_inlet = device.get_stream_inlet(timeout=1)
        signal_interface = WindowedSignal(stream_inlet, window)
        widget = SignalVisualizer(root, signal_interface, mask_controller)
        return widget
    start_widget(root2widget)
