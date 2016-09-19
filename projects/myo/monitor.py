import tkinter as tk

from eegstream.gui import Monitor
from eegstream.streaming.signal import SignalInterface

if __name__ == '__main__':
    from pylsl import resolve_byprop, StreamInlet
    from eegstream.devices import OpenBCI8
    source_id = OpenBCI8.source_id
    window = 2.0
    print("looking for a stream...")
    stream_info = resolve_byprop('source_id', source_id, timeout=1)[0]
    print(stream_info)
    stream_inlet = StreamInlet(stream_info)
    signal_interface = SignalInterface(stream_inlet, window)

    monitor = Monitor(signal_interface)
    monitor.start_mainloop()
