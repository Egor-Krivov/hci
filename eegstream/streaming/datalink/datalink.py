from abc import ABCMeta, abstractmethod


class DatalinkBase(metaclass=ABCMeta):
    """Abstract base class for data link.

    """
    @abstractmethod
    def __enter__(self):
        """Initialization process."""
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close process."""
        pass


class DatalinkTransmitter(DatalinkBase):
    """Abstract base class, supporting bytes transmission via some data link.

    """
    @abstractmethod
    def send(self, b_data):
        """Send bytes via data link."""
        pass


class DatalinkReceiver(DatalinkBase):
    """Abstract base class, supporting bytes receiving via some data link.

    """
    @abstractmethod
    def receive(self, b_data_size):
        """Receive bytes via data link."""
        pass
