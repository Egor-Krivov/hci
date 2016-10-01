import collections
from abc import ABCMeta, abstractmethod

import numpy as np
from scipy.signal import welch

from pylsl import StreamInlet, IRREGULAR_RATE


class MaskController:
    """Class, encapsulating mask logic

    Parameters
    ----------
    n_chans:
        Number of channels in signal.

    """
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


class WindowedSignal:
    """Class to hold window from stream inlet.

    Parameters
    ----------
    stream_inlet
        Stream inlet, prepared for data transmission.

    window : float
        Epoch length in seconds.
    """

    def __init__(self, stream_inlet: StreamInlet, window: float):
        self.stream_inlet = stream_inlet
        self.window = window
        stream_info = stream_inlet.info()

        self.sfreq = stream_info.nominal_srate()
        assert self.sfreq != IRREGULAR_RATE
        self.n_chans = stream_info.channel_count()
        self.epoch_len = int(self.sfreq * window)
        assert self.epoch_len > 0
        self.deque = collections.deque(maxlen=self.epoch_len)

    def __iter__(self):
        while True:
            yield self.get_epoch()

    def get_epoch(self):
        new_data = self.stream_inlet.pull_chunk(max_samples=self.epoch_len)[0]
        if new_data:
            self.deque.extend(new_data)
        return np.array(self.deque)
