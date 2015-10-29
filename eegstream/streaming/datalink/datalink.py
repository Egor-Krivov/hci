from abc import ABCMeta, abstractmethod

from eegstream.utils import grab_docs_from


class DataLinkTransmitter(metaclass=ABCMeta):
    """Class, supporting bytes transmission via some data link."""
    @abstractmethod
    def __enter__(self):
        """Initialization process."""
        return

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close process."""
        return

    @abstractmethod
    def send(self, byte_data):
        """Send bytes via data link."""
        return


class DataLinkReceiver(metaclass=ABCMeta):
    """Class, supporting bytes receiving via some data link."""
    @grab_docs_from(DataLinkTransmitter.__enter__)
    @abstractmethod
    def __enter__(self):
        return

    @grab_docs_from(DataLinkTransmitter.__exit__)
    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        return

    @abstractmethod
    def receive(self, byte_size):
        """Receive bytes via data link."""
        return
