from collections import deque

import numpy as np
from scipy.signal import welch

from eegstream.streaming import PacketReceiver


class SignalInterface:
    """Class, providing interface for signal visualization.
    Packet receiver should be activated."""
    def __init__(self, packet_receiver: PacketReceiver, channels: int,
                 freq: float=250, window: float=2):
        self.packet_receiver = packet_receiver
        self.freq = freq
        self.window = window
        self.channels = channels
        self.signal_buffer = deque(maxlen=self.get_signal_len())

    def get_signal_len(self):
        return int(self.window * self.freq)

    def get_signal(self):
        data = self.packet_receiver.receive_all()
        self.signal_buffer.extend(data)
        return self.signal_buffer

    def spectrogram(self):
        nperseg = 2**int(np.log2(self.get_signal_len()))
        while True:
            data = self.signal_buffer
            if len(data) == self.get_signal_len():
                data = np.array(data)[:, 0]
                data = welch(data, self.freq, 'flattop', nperseg,
                             scaling='spectrum')
            else:
                data = None
            yield data

    def __iter__(self):
        while True:
            self.get_signal()
            yield self.signal_buffer

if __name__ == '__main__':
    print(SignalInterface(None, 250, 2))