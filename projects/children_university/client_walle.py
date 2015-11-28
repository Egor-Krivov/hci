import sys
import time

from eegstream.devices import OpenBCI8
from eegstream.detectors import alpha_detector
from eegstream.streaming import Master
from walle_driver import WALLE


def walle_start_working_bitch(packet_receiver, port_id=1):

    port = '/dev/ttyUSB' + str(port_id)  # serial port
    baud = 9600  # baud rate

    # Instantiate WALL-E robot.
    robot = WALLE(port=port, baud=baud)
    print('Robot instantiated...', file=sys.stderr)

    # Initialize parameters.
    fs = OpenBCI8.freq
    window, step, freq_nqst, thr, thr_emg = 4*fs, fs//4, fs//2, 15, 10

    # Instantiate OpenBCI worker.

    master =  Master(packet_receiver, window, step=step):
    # Instantiate AlphaDetector.
    alpha = alpha_detector.AlphaDetector(fs, thr, thr_emg, psd_mode=True,
                                         verbose=True)
    # Instantiate EBAS.
    ebas = alpha_detector.EBAS(alpha, deque_len=(fs//step))

    while True:
        # Get actual samples as epoch.
        epoch = master.get_epoch()

        print(epoch.shape)

        # Detect stimulus with EBAS.
        y_m, stim_m, stim_emg_m = alpha.detect(epoch[6, :])  # move (red color)
        y_l, stim_l, stim_emg_l = alpha.detect(epoch[1, :])  # left (purple color)
        y_r, stim_r, stim_emg_r = alpha.detect(epoch[3, :])  # right (green color)

        print(y_m, stim_m, stim_emg_m)
        # print(y_r, stim_r, stim_emg_r)
        print('----------------------')


        # y_m = ebas.detect(epoch[7, :])  # move (red color)
        # y_l = ebas.detect(epoch[1, :])  # left (purple color)
        # y_r = ebas.detect(epoch[3, :])  # right (green color)

        if y_m:
            robot.move()
        # elif y_l:
        #     robot.left()
        # elif y_r:
        #     robot.right()
        else:
            robot.stop()

        time.sleep(0.9*(step//fs))
