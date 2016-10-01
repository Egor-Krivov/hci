import time

import numpy as np

from hci.sources import Source, source2stream_outlet


class Dummy(Source):
    """Dummy data source for testing"""
    def __init__(self, *, std=0.1, sin_freq=10, name='Dummy', type='',
                 n_chans=4, sfreq=500, source_id='Dummy'):
        super().__init__(name=name, type=type, n_chans=n_chans, sfreq=sfreq,
                         source_id=source_id)
        self.std = std
        self.sin_freq = sin_freq

    def start_streaming(self):
        stream_outlet = source2stream_outlet(self)

        T = 1 / self.sfreq
        print('Starting streaming')

        i = 0
        while True:
            i = (i + 1) % (self.sfreq * 60)
            sample = self.std * np.random.normal(size=self.n_chans) +\
                     np.sin(2 * np.pi * i * self.sin_freq / self.sfreq)
            stream_outlet.push_sample(sample)
            time.sleep(T)


if __name__ == '__main__':
    source = Dummy()
    source.start_streaming()
