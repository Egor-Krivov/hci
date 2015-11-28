from collections import deque

import numpy as np

from eegstream.streaming import PacketReceiver


class SignalInterface:
    """Signal interface class for communication

    Parameters
    ----------
    packet_receiver : PacketReceiver
        Packet receiver, prepared for data transmission.
    device : Device
        Device for the data transmission.
    window : float
        Epoch length in seconds.
    mask : iterable
        Iterable with booleans, describing channels' mask. Use all channels
        as default state.

    """

    def __init__(self, packet_receiver: PacketReceiver, device: Device,
                 window: float, mask=None, step: int=0, block_mode: bool=True,
                 verbose: bool=False):

        self.packet_receiver = packet_receiver
        self.device = device
        self.epoch_len = int(device.freq * window)
        assert self.epoch_len > 0
        self.step = step
        self._mask = [True] * device.channels if mask is None else mask
        self._mask = np.array(self._mask, dtype=bool)
        self.block_mode = block_mode
        self.verbose = verbose
        self.deque = deque(maxlen=self.epoch_len)

    def _pop_deque(self):
        """Remove from deque based buffer out of data samples."""
        for _ in range(self.step):
            self.deque.popleft()

    def __iter__(self):
        while True:
            yield self.get_epoch()

    @property
    def mask(self):
        return self._mask

    @mask.setter
    def mask(self, mask):
        mask = np.array(mask, dtype=bool)
        assert len(mask) == self.device.channels and mask.ndim == 1
        self._mask = mask
    """Class, providing interface for signal visualization.
    Packet receiver should be activated."""
    def __init__(self, packet_receiver: PacketReceiver, channels: int,
                 freq: float=250, window: float=2):
        self.packet_receiver = packet_receiver
        self.freq = freq
        self.window = window
        self.channels = channels
        self.change_mask_flag = False
        self.mask = [True] * self.channels
        self.signal_buffer = deque(maxlen=self.get_signal_len())

    def get_signal_len(self):
        return int(self.window * self.freq)

    def get_signal(self):
        data = self.packet_receiver.receive_all()
        self.signal_buffer.extend(data)
        if self.signal_buffer:
            data = np.array(self.signal_buffer).T[self.get_mask()]
        else:
            data = None
        return data

    def spectrogram(self):
        nperseg = 2**int(np.log2(self.get_signal_len()))
        while True:
            data = self.signal_buffer
            if len(data) == self.get_signal_len():
                data = np.array(data).T
                x, y = welch(data, self.freq, 'flattop', nperseg,
                             scaling='spectrum')
                y = y[self.get_mask()]
                data = x, y
            else:
                data = None
            yield data

    def get_mask(self):
        return np.array(self.mask, dtype=bool)

    def get_mask_len(self):
        return np.sum(self.get_mask())

    def change_mask(self, new_mask):
        self.mask = new_mask
        self.change_mask_flag = True

    def mask_changed(self):
        self.change_mask_flag = False

    def __iter__(self):
        while True:
            yield self.get_signal()

if __name__ == '__main__':
    print(SignalInterface(None, 250, 2))