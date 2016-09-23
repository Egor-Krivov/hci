import tkinter as tk
import numpy as np

from scipy.signal import welch

from eegstream.streaming.signal import SignalInterface, MaskController
from eegstream.gui.widgets import SignalVisualizer

class Spectrogram(SignalVisualizer):
    """Widget for signal visualization.

    Parameters
    ----------
    master : tkinter.Frame
        Container for widget.

    """

    def __init__(self, master: tk.Frame, signal_interface: SignalInterface,
                 mask_controller: MaskController):
        self.signal_interface = signal_interface
        self.n_chans = signal_interface.n_chans
        self.mask_controller = mask_controller
        super().__init__(master, signal_interface, mask_controller,
                         name='Spec', interval=75,
                         navigation_toolbar=True)
        self.x = np.linspace(0, signal_interface.window,
                             signal_interface.epoch_len)

        self.default_xlim = (0, 250)
        self.default_ylim = (0, 10)

    def animate_figure(self, y):
        """Function for animation process, called on each frame."""
        if y is not None and len(y) == self.signal_interface.epoch_len:
            mask = self.mask_controller.mask

            nperseg = 256

            self.x, self.y = welch(y.T, self.signal_interface.sfreq, 'flattop', nperseg,
                         scaling='spectrum')

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
    widget = Spectrogram(root, signal_interface, mask_controller)
    widget.pack(expand=True, fill=tk.BOTH)
    root.mainloop()
