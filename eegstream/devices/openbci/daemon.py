"""OpenBCI daemon.

Script connects to openBCI board and starts raw packet transmission.

"""
import sys
import time
from os.path import dirname, join, abspath
from contextlib import ExitStack

from eegstream.devices.openbci.open_bci_v3 import OpenBCIBoard
from eegstream.devices import OpenBCI8
from eegstream.devices.tools import make_packet_transmitter


def make_callback(packet_transmitters, save=False):
    """Callback wrapper.

    """
    # ================ #
    # Save log to file #
    # ================ #
    def callback_save(sample):
        with open(callback_save.file, 'a') as file:
            file.write(_to_str(sample))

    # Generate file name for data stream.
    cdir = join(dirname(abspath(__file__)), '../../data/')
    file = join(cdir, 'eoec-' + time.strftime('%y-%m-%d-%H-%M-%S') + '.csv')
    # Initialize attribute.
    callback_save.file = file

    # ================= #
    # Data transmission #
    # ================= #
    callback_functions = [lambda sample: t.send(sample.channel_data)
                          for t in packet_transmitters]

    if save:
        callback_functions.append(callback_save)

    return callback_functions


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


def start_streaming(transmitters, save=False):
    """Start streaming loop. Will use settings from settings file.

    Parameters
    ----------
    save : boolean
        If streaming should record data in additional logfile.

    transmitters : iterable
        Iterable with packet transmitters for connections.
        If not given, then standard path from setting file is used.

    """

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
    for t in reversed(range(1, 4)):
        print('{}...'.format(t), file=sys.stderr)
        time.sleep(1)

    with ExitStack() as stack:
        for transmitter in transmitters:
            stack.enter_context(transmitter)
        callback = make_callback(transmitters, save)

        # Start board streaming loop.
        # ==========================
        # Start packet transmission.
        # ==========================
        board.start_streaming(callback)


if __name__ == '__main__':
    save = len(sys.argv) > 1
    start_streaming(transmitters=[make_packet_transmitter(OpenBCI8)], save=save)
