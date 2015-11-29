import sys
import time

from eegstream.devices import OpenBCI8
from eegstream.detectors.alpha_detector import AlphaDetector
from eegstream.streaming import Master
from eegstream.streaming.tools import _make_packet_receiver
from walle_driver import WALLE


def start_walle(packet_receiver, device, port_id=1):

    port = '/dev/ttyUSB' + str(port_id)  # serial port
    baud = 9600  # baud rate

    # Instantiate WALL-E robot.
    robot = WALLE(port=port, baud=baud)
    print('Robot instantiated...', file=sys.stderr)

    # Initialize parameters.
    fs = device.freq
    window, step, freq_nqst, thr_emg = 4, fs//4, fs//2, 15
    # Instantiate AlphaDetector.
    alpha = AlphaDetector(fs, thr_emg, psd_mode=True)
    # Instantiate Master.
    master = Master(packet_receiver, device, window, step=step)

    for epoch in master:
        # Detect stimulus with AlphaDetector.
        y_m = alpha.detect(epoch[6, :])  # MOVE (red color)
        y_l = alpha.detect(epoch[1, :])  # LEFT (purple color)
        y_r = alpha.detect(epoch[3, :])  # RIGHT (green color)
        # Control robot thresholding parameters.
        control_robot(robot, y_m, y_l, y_r)

        print('{:1.2f}/{:1.2f}/{:1.2f}'.format(y_m, y_l, y_r), file=sys.stderr)
        print('-----------------------', file=sys.stderr)

        time.sleep(0.75*(step//fs))


def control_robot(robot, y_m, y_l, y_r):

    if y_m:
        robot.move()
    elif y_l:
        robot.left()
    elif y_r:
        robot.right()
    else:
        robot.stop()


if __name__ == '__main__':

    with _make_packet_receiver(OpenBCI8) as packet_r:
        start_walle(packet_r, OpenBCI8)
