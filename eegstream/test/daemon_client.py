import time

from eegstream.streaming import PacketReceiver


INTEGER_SIZE = 4  # integer size
MAX_NUM_OF_INTEGERS = 2**16 // INTEGER_SIZE  # max number of integer to receive

# Initialize global settings.
settings = {'packet': {'format': '8i', 'datalink_type': 'pipe'},
            'datalink': {'file': '/tmp/fifo'}}

with PacketReceiver(settings) as packet_r:

    while True:
        time.sleep(6)
        data = packet_r.receive(MAX_NUM_OF_INTEGERS//8)
        print(len(data))
