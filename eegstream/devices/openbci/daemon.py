"""OpenBCI daemon.

Script connects to openBCI board and starts raw packet transmission.

"""
import sys
import time
from os.path import dirname, join, abspath

from eegstream.devices.openbci.open_bci_v3 import OpenBCIBoard
from eegstream.devices import OpenBCI8
from eegstream.streaming.tools import _make_packet_transmitter


def make_callback(packet_transmitters, save=False):
    """Callback wrapper.

    """
    # =================
    # Save log to file.
    # =================

    def callback_save(sample):
        with open(callback_save.file, 'a') as file:
            file.write(_to_str(sample))

    # Generate file name for data stream.
    cdir = join(dirname(abspath(__file__)), '../../data/')
    file = join(cdir, 'eoec-' + time.strftime('%y-%m-%d-%H-%M-%S') + '.csv')
    # Initialize attribute.
    callback_save.file = file

    # ==================
    # Data transmission.
    # ==================

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


def start_streaming(transmitters, port_id=0, save=False, calibrate_board=None):
    """Start streaming loop. Will use settings from settings file.

    Parameters
    ----------
    save : bool
        If streaming should record data in additional logfile.

    port_id : int
        Id for ttyUSB.

    transmitters : iterable
        Iterable with packet transmitters for connections. Transmitters
        should be activated.
        If not given, then standard path from setting file is used.

    calibrate_board : callable
        Function for additional board calibration. Gets board as the only
        argument.

    """

    port = '/dev/ttyUSB' + str(port_id)  # dongle port
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

    if calibrate_board:
        calibrate_board(board)

    # Begin countdown timer.
    for t in reversed(range(1, 4)):
        print('{}...'.format(t), file=sys.stderr)
        time.sleep(1)

    callback = make_callback(transmitters, save)

    # ==========================
    # Start packet transmission.
    # ==========================

    board.start_streaming(callback)


if __name__ == '__main__':
    save = len(sys.argv) > 1
    start_streaming(transmitters=[_make_packet_transmitter(OpenBCI8)],
                    save=save)
