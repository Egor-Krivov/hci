import tkinter as tk

from scipy.signal import welch

from hci.gui.utils import start_widget
from hci.gui.widgets import SignalVisualizer
from hci.sources import Dummy
from hci.streaming.signal_interface import WindowedSignal, MaskController

class Spectrogram(SignalVisualizer):
    """Widget for signal visualization.

    Parameters
    ----------
    master : tkinter.Frame
        Container for widget.

    """

    def __init__(self, master: tk.Frame, signal_interface: WindowedSignal,
                 mask_controller: MaskController):
        self.windowed_signal = signal_interface
        self.n_chans = signal_interface.n_chans
        self.mask_controller = mask_controller
        super().__init__(master, signal_interface, mask_controller,
                         name='Spec', interval=75,
                         navigation_toolbar=True)

        self.default_xlim = (0, 250)
        self.default_ylim = (0, 10)

    def animate_figure(self, y):
        """Function for animation process, called on each frame."""
        if y is not None and len(y) == self.windowed_signal.epoch_len:
            mask = self.mask_controller.mask

            nperseg = 256

            self.x, self.y = welch(y.T, self.windowed_signal.sfreq, 'flattop',
                                   nperseg, scaling='spectrum')

            beginning = (self.x < 5)
            fifty = (self.x > 45) & (self.x < 55)
            hundred = (self.x > 95) & (self.x < 105)
            zero = fifty | hundred | beginning

            self.y = self.y.T#np.log(self.y.T)

            self.x = self.x[-zero]
            self.y = self.y[-zero]

            for i, line in enumerate(self.lines):
                if mask[i]:
                    line.set_linewidth(1)
                else:
                    line.set_linewidth(0)

                line.set_data(self.x, self.y[:, i])
            self.auto_ylim(force=True)
        return self.lines


if __name__ == '__main__':
    def root2widget(root):
        window = 1.0

        device = Dummy()
        mask_controller = MaskController(device.n_chans)
        stream_inlet = device.get_stream_inlet(timeout=1)
        signal_interface = WindowedSignal(stream_inlet, window)
        widget = Spectrogram(root, signal_interface, mask_controller)
        return widget
    start_widget(root2widget)