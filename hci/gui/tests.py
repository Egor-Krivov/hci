import time
from multiprocessing import Process

from hci.gui.utils import start_widget
from hci.gui.widgets.analyser import Analyser
from hci.gui.widgets.basic_visualizer import BasicVisualizer
from hci.gui.widgets.mask_control_api import MaskControllerAPI, MaskController
from hci.gui.widgets.signal_visualizer import SignalVisualizer
from hci.gui.widgets.spectrogram import Spectrogram
from . import Monitor, start_monitor
from hci.sources import Dummy
from hci.streaming import WindowedSignal
from hci.test import with_dummy_transmitter_setup


def check_widget(root2widget):
    sleeping_time = 0.5

    p = Process(target=start_widget, args=(root2widget,))
    p.start()
    time.sleep(sleeping_time)
    exitcode = p.exitcode
    assert exitcode is None or exitcode == 0
    p.terminate()

def test_basic_visualizer():
    check_widget(lambda root: BasicVisualizer(root))

def test_mask_controller():
    check_widget(lambda root: MaskControllerAPI(root, MaskController(4)))


def check_visualizer(visualizer):
    def root2widget(root):
        window = 1.0

        device = Dummy()
        mask_controller = MaskController(device.n_chans)
        stream_inlet = device.get_stream_inlet(timeout=1)
        signal_interface = WindowedSignal(stream_inlet, window)
        widget = visualizer(root, signal_interface, mask_controller)
        return widget
    check_widget(root2widget)

@with_dummy_transmitter_setup
def test_signal_visualizer():
    check_visualizer(SignalVisualizer)

@with_dummy_transmitter_setup
def test_spectrogram():
    check_visualizer(Spectrogram)

@with_dummy_transmitter_setup
def test_analyser():
    check_visualizer(Analyser)

@with_dummy_transmitter_setup
def test_monitor():
    sleeping_time = 0.5

    p = Process(target=start_monitor, args=(Dummy(), 1.0,))
    p.start()
    time.sleep(sleeping_time)
    exitcode = p.exitcode
    assert exitcode is None or exitcode == 0
    p.terminate()
