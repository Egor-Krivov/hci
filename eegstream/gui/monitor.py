import tkinter as tk

from eegstream.gui.widgets import MaskControllerAPI, SignalVisualizer,\
    Spectrogram

from eegstream.gui.widgets.analysis import Analyser
from eegstream.streaming.signal import SignalInterface, MaskController


class Monitor:
    def __init__(self, signal_interface: SignalInterface):
        self.root = tk.Tk()

        tk.Label(self.root, text="EEGMonitor").pack()

        n_chans = signal_interface.n_chans
        self.mask_controller = MaskController(n_chans=n_chans,
                                              mask=[False]*n_chans)

        self.signal_visualizer = SignalVisualizer(self.root,
                                                  signal_interface,
                                                  self.mask_controller)

        self.spectrogram = Spectrogram(self.root, signal_interface,
                                       self.mask_controller)

        self.analysis = Analyser(self.root, signal_interface,
                                       self.mask_controller)
        self.spectrogram.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
        self.analysis.pack(side=tk.BOTTOM, expand=tk.YES, fill=tk.BOTH)
        self.signal_visualizer.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side=tk.RIGHT, expand=tk.TRUE, fill=tk.BOTH)
        self.control_panel = MaskControllerAPI(self.right_frame,
                                          self.mask_controller)
        self.control_panel.pack(side=tk.TOP, expand=tk.FALSE, fill=tk.X)



    def start_mainloop(self):
        self.root.mainloop()

if __name__ == '__main__':
    from pylsl import resolve_byprop, StreamInlet
    from eegstream.devices import Dummy
    source_id = Dummy.source_id
    window = 1.0

    print("looking for a stream...")
    stream_info = resolve_byprop('source_id', source_id, timeout=1)[0]
    print(stream_info)
    stream_inlet = StreamInlet(stream_info)
    signal_interface = SignalInterface(stream_inlet, window)

    monitor = Monitor(signal_interface)
    monitor.start_mainloop()
