import time

from eegstream.devices import OpenBCIWorker
from eegstream.streaming import Master


worker = OpenBCIWorker()

with Master(worker, 250, step=10) as master:

    while True:
        # Get actual samples as epoch.
        epoch = master.get_epoch()
        print(epoch)
        # Emulate classifier latency, should be less then `10/250 = 0.04`.
        time.sleep(0.03)
