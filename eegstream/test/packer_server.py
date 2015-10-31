import time
import copy
import pdb
import numpy as np

from eegstream.streaming.packer import PacketTransmitter


settings = {'packet': {'fmt': 'dddd', 'mask': bytes(0b1111), 'datalink_type': 'pipe'},
            'datalink': {'file': '/tmp/fifo'}}

settings2 = copy.deepcopy(settings)
c = PacketTransmitter(settings).datalink_class
print(c)
c(settings2)


with PacketTransmitter(settings) as packet_t:
    # sleep timeout
    time.sleep(5)
    # generate random packet
    data = np.random.randint(10, 100, 4).tolist()
    packet_t.send(data)
