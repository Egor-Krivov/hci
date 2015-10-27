from abc import ABCMeta, abstractmethod


def take_docs(other_func):
    def dec(func):
        func.__doc__ = other_func.__doc__
        return func
    return dec


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
    @take_docs(DataLinkTransmitter.__enter__)
    @abstractmethod
    def __enter__(self):
        return

    @take_docs(DataLinkTransmitter.__exit__)
    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        return

    @abstractmethod
    def receive(self, byte_size):
        """Receive bytes via data link."""
        return
