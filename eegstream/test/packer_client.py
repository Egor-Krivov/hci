import time

import numpy as np

from eegstream.streaming.packet import PacketReceiver


settings = {'packet': {'format': '8ic', 'datalink_type': 'pipe'},
            'datalink': {'file': '/tmp/fifo_eegstream'}}

with PacketReceiver(settings) as packet_r:
    # Sleep timeout.
    while True:
        time.sleep(4)
        data = packet_r.receive(100)
        print(data)
