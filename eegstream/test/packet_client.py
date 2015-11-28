import time

from eegstream.streaming import Master
from eegstream.streaming.tools import _make_packet_receiver
from eegstream.devices import OpenBCI8


packet_receiver = _make_packet_receiver(OpenBCI8)

with packet_receiver:
    master = Master(packet_receiver, OpenBCI8, 1, step=10, verbose=True)
    for epoch in master:
        # Get actual samples as epoch.
        print(epoch)
        # Emulate classifier latency, should be less then `10/250 = 0.04`.
        time.sleep(0.03)
