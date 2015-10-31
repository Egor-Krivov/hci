from os.path import dirname

from eegstream.streaming import PacketReceiver
from eegstream.utils import load_settings


class Worker(PacketReceiver):
    def __init__(self):
        settings = load_settings(dirname(__file__))
        super().__init__(settings)
