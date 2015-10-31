import time

import numpy as np

from eegstream.streaming.packer import PacketReceiver


settings = {'packet': {'fmt': 'dddd', 'mask': bytes(0b1111), 'datalink_type': 'pipe'},
            'datalink': {'file': '/tmp/fifo'}}

with PacketReceiver(settings) as packet_r:
    # sleep timeout
    time.sleep(0.001)
    data = packet_r.receive(10)
    print(data)
