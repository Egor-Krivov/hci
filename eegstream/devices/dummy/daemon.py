import time

import numpy as np
from pylsl import StreamOutlet

from eegstream.devices import Dummy, make_stream_info


def start_streaming(outlet: StreamOutlet):
    std = 0.1

    sfreq = Dummy.sfreq
    T = 1 / sfreq
    n_chans = Dummy.n_chans
    print('Starting streaming')
    i = 0
    while True:
        i = (i + 1) % (sfreq * 60)
        sample = std * np.random.normal(size=n_chans) + np.sin(2 * np.pi * i/50)
                 #np.random.normal(size=n_chans)

        outlet.push_sample(sample)
        time.sleep(T)


if __name__ == '__main__':
    stream_info = make_stream_info(Dummy)
    outlet = StreamOutlet(stream_info)
    start_streaming(outlet)
