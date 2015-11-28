import time

from eegstream.streaming.tools import _make_packet_transmitter
from eegstream.devices import OpenBCI8


i = 0
with _make_packet_transmitter(OpenBCI8) as packet_t:

    while True:
        # Sleep timeout.
        time.sleep(1/250)
        # Generate random packet.
        data = [i]*8
        i += 1
        i %= 256
        packet_t.send(data)
        print(data)
