"""OpenBCI worker.

Worker class is used to communicate with OpenBCI board.

"""
from os.path import dirname
import warnings

from eegstream.streaming import PacketReceiver
from eegstream.utils import load_settings


class Worker(PacketReceiver):
    """Worker class for OpenBCI.

    """
    def __init__(self):
        warnings.warn("deprecated, use make_receiver(device=OpenBCI8) from "
                      "eegstream.devices instead", DeprecationWarning)
        settings = load_settings(dirname(__file__))
        super().__init__(settings)
