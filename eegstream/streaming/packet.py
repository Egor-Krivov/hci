import struct
from abc import abstractmethod, ABCMeta

from .datalink import FifoTransmitter, FifoReceiver
from .datalink.datalink import DatalinkBase


class PacketBase(metaclass=ABCMeta):
    """Abstract base class for packet.

    """
    def __init__(self, settings):
        # Remove packet settings from global settings dictionary. Due to the
        # hierarchical structure, lower level blocks do not require information
        # from higher level settings.
        self.settings = settings.pop('packet', None)
        self.deeper_settings = settings

        if not self.settings:
            # Happens, when settings, passed to the packer were incorrect
            # and doesn't content settings for packer at all.
            raise ValueError('Failed to unpack packet settings')

        # Unpack useful settings.
        self.fmt = self.settings['format']
        self.datalink_type = self.settings['datalink_type']

        # Calculate packet size.
        self.packet_size = struct.calcsize(self.fmt)

    @property
    @abstractmethod
    def datalink_class(self):
        print('111111111111111111111111111111111111111')
        return DatalinkBase

    def __enter__(self):
        self.datalink = self.datalink_class(self.deeper_settings)
        self.datalink.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.datalink.__exit__(exc_type, exc_val, exc_tb)


class PacketTransmitter(PacketBase):
    """Class sends tuplet with basic python types via given data link.

    Parameters
    ----------
    settings : dict
        Settings for streaming part on current level and below. Will take
        packet settings from global settings dictionary and push everything
        else deeper.
        This class requires:
            fmt: string
                Setting, describing data in tuplet.
            datalink_type: str
                Data link type, one of the following:
                'pipe': will use named pipe.

    """
    @property
    def datalink_class(self):
        if self.datalink_type == 'pipe':
            return FifoTransmitter
        else:
            # Packer couldn't understand datalink type, provided in settings
            raise ValueError('Unknown datalink type {}'.
                             format(self.datalink_type))

    def send(self, packet):
        """Send packets in non-blocking mode.

        Parameters
        ----------
        packet : iterable
            Iterable with data organized according to fmt settings.

        Raises
        ------
        exception.BrokenPipeError
            Raises when pipe is broken. For example, when there is no one on
            the reading side.

        """
        raw_packet = struct.pack(self.fmt, *packet)
        return self.datalink.send(raw_packet)


class PacketReceiver(PacketBase):
    """Class receives tuplets with basic python types via given data link.

    Parameters
    ----------
    settings : dict
        Settings for streaming part on current level and below. Will take
        packet settings from global settings dictionary and push everything
        else deeper.
        This class requires:
            fmt: string
                setting, describing data in tuplets.
            datalink_type: str
                Data link type, one of the following:
                'pipe': will use named pipe.

    """
    @property
    def datalink_class(self):
        if self.datalink_type == 'pipe':
            return FifoReceiver
        else:
            # Packer couldn't understand datalink type, provided in settings
            raise ValueError('Unknown datalink type {}'.
                             format(self.datalink_type))

    def receive(self, packet_count):
        """Receive packets in non-blocking mode.

        Parameters
        ----------
        packet_count : int
            Maximum number of packets to gather.

        Returns
        -------
        packets : list
            Packets with data in given form fmt.

        """
        raw_data = self.datalink.receive(packet_count * self.packet_size)

        # Calculate packet count and reminder.
        packet_count, reminder = divmod(len(raw_data), self.packet_size)

        # This shouldn't happen at all, currently (with pipe)
        assert reminder == 0, ('Incomplete number of bytes were found in data.\n'
                               'Got {} packets and remider is {}'.
                               format(packet_count, reminder))

        raw_data = [raw_data[i * self.packet_size:(i + 1) * self.packet_size]
                    for i in range(packet_count)]
        packets = [struct.unpack(self.fmt, raw_packet)
                   for raw_packet in raw_data]

        return packets
