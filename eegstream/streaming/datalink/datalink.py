from abc import ABCMeta, abstractmethod


class DatalinkBase(metaclass=ABCMeta):
    """Abstract base class for data link.

    """
    @abstractmethod
    def __init__(self, settings):
        """Initialization process with settings parameter."""
        # Pop data link settings from global settings dictionary. Due to the
        # hierarchical structure, lower level do not require information from
        # higher level settings.
        self.settings = settings.pop('datalink', None)

        if not self.settings:
            # Data link settings were incorrect.
            raise ValueError('Failed to unpack data link settings')

    @abstractmethod
    def __enter__(self):
        """Data link initialization process."""
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Data link close process."""
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
