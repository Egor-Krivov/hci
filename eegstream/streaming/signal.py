from collections import deque

import numpy as np
from scipy.signal import welch

from pylsl import StreamInlet

class MaskController:
    def __init__(self, n_chans, mask=None):
        self.n_chans = n_chans
        if mask is None:
            mask = [True] * self.n_chans
        self._mask = np.array(mask)

    @property
    def mask(self):
        return self._mask

    @mask.setter
    def mask(self, new_mask):
        assert self.n_chans == len(new_mask)
        self._mask = np.array(new_mask)

class SignalInterface:
    """Signal interface class for communication

    Parameters
    ----------
    stream_inlet
        Stream inlet, prepared for data transmission.
    sfreq
        Signal frequency in seconds.
    window : float
        Epoch length in seconds.
    n_chans
        Number of channels in signal.

    """

    def __init__(self, stream_inlet: StreamInlet, window: float):
        self.stream_inlet = stream_inlet
        self.window = window
        stream_info = stream_inlet.info()

        self.sfreq = stream_info.nominal_srate()
        self.n_chans = stream_info.channel_count()
        self.epoch_len = int(self.sfreq * window)
        assert self.epoch_len > 0
        self.deque = deque(maxlen=self.epoch_len)

    def __iter__(self):
        while True:
            yield self.get_epoch()

    def get_epoch(self):
        new_data = self.stream_inlet.pull_chunk(max_samples=self.epoch_len)[0]
        if new_data:
            self.deque.extend(new_data)
        return np.array(self.deque)

    def spectrogram(self):
        nperseg = 2**int(np.log2(self.epoch_len))
        while True:
            data = self.get_epoch()
            if len(data) == self.epoch_len:
                data = data[:, [False, ]]
                data = np.array(data).T
                x, y = welch(data, self.sfreq, 'flattop', nperseg,
                             scaling='spectrum')
                data = x, y.T
            else:
                data = None
            yield data

if __name__ == '__main__':
    from pylsl import resolve_byprop, StreamInlet
    from eegstream.devices import Dummy
    import time
    source_id = Dummy.source_id
    window = 1.0

    print("looking for a stream...")
    stream_info = resolve_byprop('source_id', source_id, timeout=1)[0]
    print(stream_info)
    stream_inlet = StreamInlet(stream_info)
    signal_interface = SignalInterface(stream_inlet, window)
    for data in signal_interface:
        if data is not None:
            print(data.shape)
        time.sleep(0.1)