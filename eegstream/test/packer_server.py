import time
import copy
import pdb
import numpy as np

from eegstream.streaming.packet import PacketTransmitter

import cProfile

cProfile.run("""
settings = {'packet': {'format': '19ic', 'datalink_type': 'pipe'},
            'datalink': {'file': '/tmp/fifo'}}

i = 0
with PacketTransmitter(settings) as packet_t:
    while True:
        # sleep timeout
        time.sleep(0.0001)
        # generate random packet

        data = [i] * 19 + [b'0']
        i += 1
        i %= 256
        packet_t.send(data)
        print(data)
""")
