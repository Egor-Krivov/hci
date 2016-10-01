import sys
import time

from hci.sources import source2stream_info, Source
from hci.sources.openbci.open_bci_driver import OpenBCIBoard

from pylsl import StreamInfo, StreamOutlet


class OpenBCI(Source):
    """OpenBCI board with 8 channels and frequency 250Hz.

    Parameters
    ----------
    port_id :
        Id for ttyUSB.

    save_path :
        If streaming should record data in additional logfile.
    """
    def __init__(self, *, port_id=0, save_path: str=None, name='OpenBCI',
                 type='', source_id='OpenBCI'):
        self.port_id = port_id
        self.save_path = save_path

        n_chans = 8
        sfreq = 250
        super().__init__(name=name, type=type, n_chans=n_chans, sfreq=sfreq,
                         source_id=source_id)

    def start_streaming(self):
        stream_outlet = self.get_stream_outlet()
        start_bci_streaming(stream_outlet, self.port_id, self.save_path)


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


def start_bci_streaming(outlet: StreamOutlet, port_id: int=0, save_path: str=None,
                    calibrate_board=None):
    """Start streaming loop. Will use settings from settings file.

    Parameters
    ----------
    outlet :
        Outlet to push samples.

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
    stream_info = source2stream_info(OpenBCI8)
    stream_outlet = StreamOutlet(stream_info)
    start_streaming(stream_outlet)