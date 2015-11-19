"""OpenBCI daemon.

Script connects to openBCI board and starts raw packet transmission.

"""
import os.path as pa
import sys
import time

import numpy as np

from open_bci_v3 import OpenBCIBoard
from eegstream.streaming import PacketTransmitter
from eegstream.utils import load_settings


def make_callback(packet_t, save=False):
    """Callback wrapper.

    """
    def callback(sample):
        packet_t.send(sample.channel_data)

    def callback_save(sample):
        with open(callback_save.file, 'a') as file:
            file.write(_to_str(sample))

    # Generate file name for data stream.
    cdir = pa.join(pa.dirname(pa.abspath(__file__)), '../../data/')
    file = pa.join(cdir, 'eoec-' + time.strftime('%y-%m-%d-%H-%M-%S') + '.csv')
    # Initialize attribute.
    callback_save.file = file

    return [callback, callback_save] if save else callback


def _to_str(sample):
    sid = sample.id
    eeg = sample.channel_data
    aux = sample.aux_data

    # Parse time data.
    raw = ['{:.0f}'.format(sid)]
    # Parse eeg data.
    raw.extend(['{:.6f}'.format(x) for x in eeg])
    # Parse auxiliary data.
    raw.extend(['{:.3f}'.format(x) for x in aux])

    return ','.join(x for x in raw) + '\n'


if __name__ == '__main__':
    port = '/dev/ttyUSB0'  # dongle port
    baud = 115200  # serial port baud rate

    # =================
    # Connect to board.
    # =================

    # Instantiate board.
    board = OpenBCIBoard(port=port, baud=baud, filter_data=False,
                         scaled_output=True, log=False)
    print('Board instantiated...')
    # Soft reset for the board peripherals. The 8bit board gets a reset signal
    # from the dongle any time an application opens the serial port, just like
    # an arduino. The 32bit board doesn't have this feature. To reset the 32bit
    # board program should send it a `v`.
    board.ser.write(b'v')
    # Wait reasonable amount of time to establish stable connection.
    time.sleep(5)
    # Begin countdown timer.
    for t in range(5, 0, -1):
        print('{}...'.format(t), file=sys.stderr)
        time.sleep(1)

    # ==========================
    # Start packet transmission.
    # ==========================

    # Initialize global settings.
    settings = load_settings(pa.dirname(__file__))
    # Initialize script settings.
    save = False if len(sys.argv) == 1 else True

    with PacketTransmitter(settings) as packet_t:
        # Get callback function.
        callback = make_callback(packet_t, save)
        # Start board streaming.
        board.start_streaming(callback)
