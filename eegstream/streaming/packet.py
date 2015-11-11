import struct
from abc import abstractmethod, ABCMeta

from .datalink import FifoTransmitter, FifoReceiver
from .datalink.datalink import DatalinkBase


class PacketBase(metaclass=ABCMeta):
    """Abstract base class for packet.

    """
    def __init__(self, settings):
        # Pop packet settings from global settings dictionary. Due to the
        # hierarchical structure, lower level do not require information from
        # higher level settings.
        self.settings = settings.pop('packet', None)
        self.deeper_settings = settings

        if not self.settings:
            # Packet settings were incorrect.
            raise ValueError('Failed to unpack packet settings')

        # Unpack useful settings.
        self.fmt = self.settings['format']
        self.datalink_type = self.settings['datalink_type']
        # Calculate packet size.
        self.packet_size = struct.calcsize(self.fmt)

    @property
    @abstractmethod
    def datalink_class(self):
        return DatalinkBase

    def __enter__(self):
        self.datalink = self.datalink_class(self.deeper_settings)
        self.datalink.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.datalink.__exit__(exc_type, exc_val, exc_tb)


class PacketTransmitter(PacketBase):
    """Class sends packet with basic python types via given data link.

    Parameters
    ----------
    settings : dict
        Settings for data streaming on current hierarchical level and below.
        Will pop packet settings from global settings dictionary and push
        everything else deeper. This class requires:
            fmt : string
                Data format in packet.
            datalink_type : str
                Data link type, one of the following:
                'pipe': will use named pipe.

    """
    @property
    def datalink_class(self):
        if self.datalink_type == 'pipe':
            return FifoTransmitter
        else:
            # Unknown datalink type provided in settings.
            raise ValueError('Unknown datalink type {}'.
                             format(self.datalink_type))

    def send(self, packet):
        """Send packet in non-blocking mode.

        Parameters
        ----------
        packet : iterable
            Iterable with data organized according to `fmt` setting.

        Returns
        -------
        b_data_size : int
            Number of bytes actually written. Can be zero, if nothing is
            written.

        Raises
        ------
        exception.BrokenPipeError
            Raises when the FIFO is broken. For example, when there is no one
            on the reading side.

        """
        b_data = struct.pack(self.fmt, *packet)
        return self.datalink.send(b_data)


class PacketReceiver(PacketBase):
    """Class receives packets with basic python types via given data link.

    Parameters
    ----------
    settings : dict
        Settings for data streaming on current hierarchical level and below.
        Will pop packet settings from global settings dictionary and push
        everything else deeper. This class requires:
            fmt : string
                Data format in packet.
            datalink_type : str
                Data link type, one of the following:
                'pipe': will use named pipe.

    """
    @property
    def datalink_class(self):
        if self.datalink_type == 'pipe':
            return FifoReceiver
        else:
            # Unknown datalink type provided in settings.
            raise ValueError('Unknown datalink type {}'.
                             format(self.datalink_type))

    def receive(self, n_packets):
        """Receive packets in non-blocking mode.

        Parameters
        ----------
        n_packets : int
            Number of packets to receive at most.

        Returns
        -------
        packets : list
            Packets with data in given format according to `fmt` setting.

        """
        b_data = self.datalink.receive(n_packets*self.packet_size)

        # Calculate number of received packets (full packets) and reminder
        # (broken packet's part). Normally, reminder must be zero indicating
        # that none of the received packets has been lost.
        n_packets, reminder = divmod(len(b_data), self.packet_size)
        # This shouldn't happen at all, currently (with the FIFO)
        assert reminder == 0, ('Broken packet: reminder={}'.format(reminder))

        # Parse binary data into chunks corresponding to the packet format.
        b_data_list = [b_data[i*self.packet_size:(i+1)*self.packet_size]
                       for i in range(n_packets)]

        # Unpack binary chunks to real packets according to the given format.
        packets = [struct.unpack(self.fmt, b_data) for b_data in b_data_list]

        return packets
