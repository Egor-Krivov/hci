"""OpenBCI worker.

Worker class is used to communicate with OpenBCI board.

"""
import warnings

from .devices import OpenBCI8
from eegstream.streaming import PacketReceiver


class Worker(PacketReceiver):
    """Worker class for OpenBCI.

    """
    def __init__(self):
        warnings.warn("deprecated, use make_receiver(device=OpenBCI8) from "
                      "eegstream.devices instead", DeprecationWarning)
        settings = OpenBCI8().get_default_settings()
        super().__init__(settings)