import struct
import itertools

from .datalink import PipeTransmitter, PipeReceiver


class PacketTransmitter:
    """Class sends tuplets with basic python types via given data link.

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
            self.data_link_transmitter = PipeTransmitter(self.deeper_settings)
        else:
            raise ValueError('Unknown data_link_type {}'.format(
                self.data_link_type
            ))

        self.data_link_transmitter.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.data_link_transmitter.__exit__(exc_type, exc_val, exc_tb)

    def send(self, packets):
        """Send packets

        Parameters
        ----------
        packets : iterable
            Iterable with tuplets organized according to fmt settings
        """
        raw_data = [struct.pack(self.fmt, *data) for data in packets]
        list(itertools.chain(*raw_data))
