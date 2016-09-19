"""OpenBCI daemon.

Script connects to openBCI board and starts raw packet transmission.

"""
import sys
import time

from eegstream.devices import make_stream_info
from eegstream.devices.openbci.open_bci_v3 import OpenBCIBoard
from eegstream.devices.openbci import OpenBCI8

from pylsl import StreamInfo, StreamOutlet


def make_callback(outlet: StreamOutlet, *, save_path: str=None):
    """Callback wrapper.

    """
    # =================
    # Save log to file.
    # =================

    def callback_save(sample):
        with open(save_path, 'a') as file:
            file.write(sample_to_str(sample))

    # ==================
    # Data transmission.
    # ==================

    def push(x):
        outlet.push_sample(x.channel_data)

    callback_functions = [push]

    if save_path:
        callback_functions.append(callback_save)

    return callback_functions


def sample_to_str(sample):
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


def start_streaming(outlet: StreamOutlet, port_id: int=0, save_path: str=None,
                    calibrate_board=None):
    """Start streaming loop. Will use settings from settings file.

    Parameters
    ----------
    outlet :
        Iterable with outlet for connection.

    port_id :
        Id for ttyUSB.

    save_path :
        If streaming should record data in additional logfile.

    calibrate_board :
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
    #time.sleep(2)

    # Why is that?
    if calibrate_board:
        calibrate_board(board)

    # Begin countdown timer.
    for t in reversed(range(1, 4)):
        print('{}...'.format(t), file=sys.stderr)
        time.sleep(1)

    # ==========================
    # Start packet transmission.
    # ==========================
    callback = make_callback(outlet, save_path=save_path)
    board.start_streaming(callback)


if __name__ == '__main__':
    stream_info = make_stream_info(OpenBCI8)
    stream_outlet = StreamOutlet(stream_info)
    start_streaming(stream_outlet)