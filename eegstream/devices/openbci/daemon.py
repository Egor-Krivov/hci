import time

from .open_bci_v3 import OpenBCIBoard
from eegstream.streaming import PacketTransmitter


def make_callback(packet_t):
    """Callback wrapper.

    """
    def callback(vsample):
        print('packet {}'.format(vsample.channel_data))
        print('type {}'.format(vsample.channel_data[0].type))
        packet_t.send(vsample.channel_data)

    return callback


if __name__ == '__main__':
    port = '/dev/ttyUSB0'  # dongle port
    baud = 115200  # serial port baud rate

    # Instantiate board.
    board = OpenBCIBoard(port=port, baud=baud, filter_data=False,
                         scaled_output=True, log=False)
    print('Board Instantiated')

    # Soft reset for the board peripherals. The 8bit board gets a reset signal
    # from the dongle any time an application opens the serial port, just like
    # an arduino. the 32bit board doesn't have this feature. So, if you want to
    # soft-reset the 32bit board, send it a `v`.
    board.ser.write('v')

    # Wait reasonable amount of time to establish stable connection.
    time.sleep(10)

    # Initialize global settings.
    settings = {'packet': {'format': '8i', 'datalink_type': 'pipe'},
                'datalink': {'file': '/tmp/fifo'}}

    # Begin packet transmission.
    with PacketTransmitter(settings) as packet_t:
        # Get callback function.
        callback = make_callback(packet_t)
        # Start board streaming.
        board.start_streaming(callback)
