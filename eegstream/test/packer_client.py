import time

import numpy as np

from eegstream.streaming.packer import PacketReceiver


settings = {'packet': {'fmt': '19ic', 'mask': bytes(0b1111), 'datalink_type': 'pipe'},
            'datalink': {'file': '/tmp/fifo'}}

with PacketReceiver(settings) as packet_r:
    # sleep timeout
    while True:
        time.sleep(6)
        data = packet_r.receive(40000)
        print(len(data))
