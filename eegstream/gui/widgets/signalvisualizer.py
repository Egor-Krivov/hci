import tkinter as tk

import numpy as np

from matplotlib.lines import Line2D

from eegstream.gui.widgets.basic_visualizer import BasicVisualizer
from eegstream.streaming.signal import SignalInterface, MaskController

class SignalVisualizer(BasicVisualizer):
    """Widget for signal visualization.

    Parameters
    ----------
    master
        Container for widget.

    signal_interface
        Provides data for the animation, should return list of new values.

    """
    def __init__(self, master: tk.Frame, signal_interface: SignalInterface,
                 mask_controller: MaskController, name='Signal Visualizer',
                 interval=75, navigation_toolbar=True):
        self.signal_interface = signal_interface
        self.n_chans = signal_interface.n_chans
        self.mask_controller = mask_controller

        super().__init__(master, name=name, interval=interval,
                         data_source=signal_interface,
                         navigation_toolbar=navigation_toolbar)

        self.default_xlim = (0, self.signal_interface.window)
        self.default_ylim = (-2, 2)

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
        self.y = None
        return self.lines

    def animate_figure(self, y):
        """Function for animation process, called on each frame."""
        if y is not None and len(y) > 0:
            self.x = np.linspace(0, self.signal_interface.window, len(y))
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
    from pylsl import resolve_byprop, StreamInlet
    from eegstream.devices import Dummy

    source_id = Dummy.source_id
    window = 1.0

    print("looking for a stream...")
    stream_info = resolve_byprop('source_id', source_id, timeout=1)[0]
    print(stream_info)
    mask_controller = MaskController(Dummy.n_chans)
    stream_inlet = StreamInlet(stream_info)
    signal_interface = SignalInterface(stream_inlet, window)

    root = tk.Tk()
    widget = SignalVisualizer(root, signal_interface, mask_controller)
    widget.pack(expand=True, fill=tk.BOTH)
    root.mainloop()
