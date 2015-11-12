import time
import copy
import pdb
import numpy as np

from eegstream.streaming.packet import PacketTransmitter

settings = {'packet': {'format': '8d', 'datalink_type': 'pipe'},
            'datalink': {'file': '/tmp/fifo_eegstream'}}

i = 0
with PacketTransmitter(settings) as packet_t:

    while True:
        # Sleep timeout.
        time.sleep(1/250)
        # Generate random packet.
        data = [i]*8
        i += 1
        i %= 256
        packet_t.send(data)
        print(data)
