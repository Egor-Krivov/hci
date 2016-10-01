from multiprocessing import Process
import time

from pylsl import StreamInlet

from hci.sources.dummy import Dummy
from hci.test import with_dummy_transmitter_setup

@with_dummy_transmitter_setup
def test_dummy_transmit():
    time.sleep(0.5)

@with_dummy_transmitter_setup
def test_dummy_receive():
    device = Dummy()

    waiting_time = 0.2
    inlet = device.get_stream_inlet(timeout=1)
    for i in range(3):
        time.sleep(waiting_time)
        data, timestamps = inlet.pull_chunk()
    receive_factor = len(data) / device.sfreq / waiting_time
    assert 0.5 < receive_factor < 1

