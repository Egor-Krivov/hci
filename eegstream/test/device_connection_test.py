from time import sleep

import numpy as np
import eegstream.streaming as streaming
import eegstream.devices as devices

t, r = streaming.make_packet_connection(devices.OpenBCI8)
with r, t:
    while True:
        x = np.random.randn(8)
        print('sending ', list(x))
        t.send(x)
        y = r.receive(1000)
        assert(len(y) == 1)
        y = y[0]
        print('received ', y)
        sleep(1)
