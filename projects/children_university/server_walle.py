import time

from eegstream.devices.openbci.daemon import start_streaming
from eegstream.streaming.tools import _make_packet_transmitter
from eegstream.devices.openbci import OpenBCI8


def setup_channel(board, chan, params):
    """Setups channel setting commands.

    """
    board.ser.write(b'x')
    time.sleep(0.1)
    board.ser.write(bytes(chan, 'ascii'))
    time.sleep(0.1)

    for s in str(params):
        board.ser.write(bytes(s, 'ascii'))
        time.sleep(0.1)

    board.ser.write(b'X')
    time.sleep(0.1)


def calibrate_board(board):
    # Channel setting commands.
    #
    # CHANNEL        : 1 2 3 4 5 6 7 8 Q W E R T Y U I
    # POWER_DOWN     : 0\1 = ON\OFF (0 default)
    # GAIN_SET       : 0 1 2 3 4 5 6 (6 default)
    # INPUT_TYPE_SET : 0 (ADSINPUT_NORMAL default)
    # BIAS_SET       : 0\1 = Remove\include from\in BIAS (1 default)
    # SRB2_SET       : 0\1 = Dis\connect this input from\to SRB2 (1 default)
    # SRB1_SET       : 0\1 = Dis\connect all inputs from\to SRB1 (0 default)

    setup_channel(board, '1', '100000')
    setup_channel(board, '2', '060000')  # ON
    setup_channel(board, '3', '100000')
    setup_channel(board, '4', '160000')  # ON
    setup_channel(board, '5', '100000')
    setup_channel(board, '6', '100000')
    setup_channel(board, '7', '060000')  # ON
    setup_channel(board, '8', '100000')


def start_walle_streaming(transmitters, port_id):
    start_streaming(transmitters, port_id, calibrate_board=calibrate_board)


if __name__ == '__main__':
    port_id = 0
    packet_transmitter = _make_packet_transmitter(OpenBCI8)

    with packet_transmitter:
        start_walle_streaming([packet_transmitter], port_id)
