"""OpenBCI daemon.

Script connects to openBCI board and starts raw packet transmission.

"""
import sys
import time
from copy import deepcopy
from os.path import dirname, join, abspath
from contextlib import ExitStack

from eegstream.devices.openbci.open_bci_v3 import OpenBCIBoard
from eegstream.streaming import PacketTransmitter
from eegstream.utils import load_settings


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


def start_streaming(save=False, filenames=None):
    """Start streaming loop. Will use settings from settings file.

    Parameters
    ----------
    save : boolean
        If streaming should record data in additional logfile.

    filenames : iterable
        Iterable with strings, describing paths to fifo files.
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
    for t in reversed(range(0, 6)):
        print('{}...'.format(t), file=sys.stderr)
        time.sleep(1)

    # ==========================
    # Start packet transmission.
    # ==========================

    # Initialize global settings.
    standard_settings = load_settings(dirname(__file__))
    # Initialize script settings.

    settings_list = []
    if not filenames:
        filenames = [standard_settings['datalink']['file']]

    for filename in filenames:
        file_settings = deepcopy(standard_settings)
        file_settings['datalink']['file'] = filename
        settings_list.append(file_settings)

    with ExitStack() as stack:
        transmitters = []
        # Instantiate transmitters
        for settings in settings_list:
            transmitter = stack.enter_context(PacketTransmitter(settings))
            transmitters.append(transmitter)

        callback = make_callback(transmitters, save)
        # Start board streaming loop.
        board.start_streaming(callback)


if __name__ == '__main__':
    save = len(sys.argv) > 1
    start_streaming(save=save)
