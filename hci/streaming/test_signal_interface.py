import time

from hci.test import with_dummy_transmitter_setup
from hci.sources import Dummy
from .signal_interface import WindowedSignal, MaskController


@with_dummy_transmitter_setup
def test_signal_interface():
    window = 0.1
    tol = 0.1

    device = Dummy()
    stream_inlet = device.get_stream_inlet(timeout=1)
    signal_interface = WindowedSignal(stream_inlet, window)

    data = signal_interface.get_epoch()
    time.sleep(window)
    data = signal_interface.get_epoch()

    for i in range(3):
        time.sleep(window)
        data = signal_interface.get_epoch()
        relative_val = (len(data)-device.sfreq*window) / device.sfreq*window
        assert abs(relative_val) < tol

def test_mask_controller():
    n_chans = 3
    mask_controller = MaskController(n_chans=n_chans)
    mask_controller.mask = [True, False, True]
    mask = mask_controller.mask
    assert mask[0] and not mask[1] and mask[2]


