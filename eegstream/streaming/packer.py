import struct

from .datalink import PipeTransmitter, PipeReceiver


class PacketTransmitter:
    """Class sends tuplet with basic python types via given data link.

    Parameters
    ----------
    settings : dict
        Settings for streaming part on current level and below. Will take
        settings['packet'] field and push everything else deeper.
        This class requires:
            fmt: string
                setting, describing data in tuplet.
            data_link_type: str
                Data link type, one of the following:
                    'pipe': will use named pipe.

    """
    def __init__(self, settings):
        self.settings = settings.pop('packet', None)
        if not self.settings:
            raise ValueError('Packet transmitter got empty settings')
        self.fmt = self.settings['fmt']
        self.packet_size = struct.calcsize(self.fmt)
        self.data_link_type = self.settings['data_link_type']
        self.deeper_settings = settings

    def __enter__(self):
        if self.data_link_type == 'pipe':
            self.data_link_transmitter = PipeTransmitter(self.deeper_settings)
        else:
            raise ValueError('Unknown data_link_type {}'.format(
                self.data_link_type
            ))

        self.data_link_transmitter.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.data_link_transmitter.__exit__(exc_type, exc_val, exc_tb)

    def send(self, packet):
        """Send packet

        Parameters
        ----------
        packets : iterable
            Iterable with tuplet organized according to fmt settings
        """
        raw_packet = struct.pack(self.fmt, *packet)
        return self.data_link_transmitter.send(raw_packet)


class PacketReceiver:
    """Class receives tuplets with basic python types via given data link.

    Parameters
    ----------
    settings : dict
        Settings for streaming part on current level and below. Will take
        settings['packet'] field and push everything else deeper.
        This class requires:
            fmt: string
                setting, describing data in tuplets.
            data_link_type: str
                Data link type, one of the following:
                    'pipe': will use named pipe.

    """
    def __init__(self, settings):
        self.settings = settings.pop('packet', None)
        if not self.settings:
            raise ValueError('Packet transmitter got empty settings')
        self.fmt = self.settings['fmt']
        self.packet_size = struct.calcsize(self.fmt)
        self.data_link_type = self.settings['data_link_type']
        self.deeper_settings = settings

    def __enter__(self):
        if self.data_link_type == 'pipe':
            self.data_link_receiver = PipeReceiver(self.deeper_settings)
        else:
            raise ValueError('Unknown data_link_type {}'.format(
                self.data_link_type
            ))

        self.data_link_receiver.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.data_link_receiver.__exit__(exc_type, exc_val, exc_tb)

    def receive(self, packet_count):
        """Receive packets in non-blocking mode.

        Parameters
        ----------
        packet_count : int
            Maximum number of packets to gather.

        Returns
        -------
        packets : list
            packets with data in given form fmt
        """
        raw_data = self.data_link_receiver.receive(
            packet_count * self.packet_size)

        packet_count, reminder = divmod(len(raw_data), self.packet_size)
        assert reminder == 0, 'Incomplete number of bytes were found in data' \
                              ' link layer reminder is {}'.format(reminder)

        raw_data = [raw_data[i * self.packet_size: (i + 1) * self.packet_size]
                    for i in range(packet_count)]
        packets = [struct.unpack(self.fmt, raw_packet)
                   for raw_packet in raw_data]
        return packets
