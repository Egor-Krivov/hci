import tkinter as tk
import numpy as np
from collections import deque

from scipy.signal import welch

from eegstream.streaming.signal import SignalInterface, MaskController
from eegstream.gui.widgets.basic_visualizer import BasicVisualizer

from eegstream.detectors import build_analyser

class Analyser(BasicVisualizer):
    """Widget for signal visualization.

    Parameters
    ----------
    master
        Container for widget.

    signal_interface
        Provides data for the animation, should return list of new values.

    """
    def __init__(self, master: tk.Frame, signal_interface: SignalInterface,
                 mask_controller: MaskController, name='Gesture',
                 interval=50, navigation_toolbar=True):
        self.signal_interface = signal_interface
        self.n_chans = signal_interface.n_chans
        self.mask_controller = mask_controller

        self.button = tk.Button(master, text='Activate analysis', command=self.build_predictor)
        self.button.pack(side=tk.TOP)

        super().__init__(master, name=name, interval=interval,
                         data_source=signal_interface,
                         navigation_toolbar=navigation_toolbar)

        self.default_xlim = (0, self.signal_interface.window)
        self.default_ylim = (-0.3, 1.3)

        self.x = np.linspace(0, self.signal_interface.window,
                             int(signal_interface.window / interval * 1000))

        self.predictor = None

    def build_predictor(self, name='online'):
        self.predictor = build_analyser(name=name)

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

    def animate_figure(self, y):
        """Function for animation process, called on each frame."""
        if y is not None and len(y) == self.signal_interface.epoch_len and self.predictor is not None:

            self.y.append(self.predictor(y))

            if len(self.y) == len(self.x):
                self.lines[0].set_data(self.x, self.y)
        return self.lines


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
    widget = Analyser(root, signal_interface, mask_controller)
    widget.pack(expand=True, fill=tk.BOTH)
    root.mainloop()
