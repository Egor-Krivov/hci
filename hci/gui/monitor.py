import tkinter as tk


from hci.sources import Dummy, Source
from hci.gui.widgets import MaskControllerAPI, SignalVisualizer,\
    Spectrogram, Analyser
from hci.streaming.signal_interface import WindowedSignal, MaskController


class Monitor:
    def __init__(self, windowed_signal: WindowedSignal):
        self.root = tk.Tk()

        tk.Label(self.root, text="Monitor").pack()

        n_chans = windowed_signal.n_chans
        self.mask_controller = MaskController(n_chans=n_chans,
                                              mask=[True]*n_chans)

        self.signal_visualizer = SignalVisualizer(self.root,
                                                  windowed_signal,
                                                  self.mask_controller)

        self.spectrogram = Spectrogram(self.root, windowed_signal,
                                       self.mask_controller)

        self.analysis = Analyser(self.root, windowed_signal=windowed_signal,
                                 mask_controller=self.mask_controller)
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

def start_monitor(source: Source, window):
    stream_inlet = source.get_stream_inlet(timeout=1)
    signal_interface = WindowedSignal(stream_inlet, window)

    monitor = Monitor(signal_interface)
    monitor.start_mainloop()

if __name__ == '__main__':
    start_monitor(Dummy(), 1.0)
