from multiprocessing import Process
from time import sleep

import numpy as np

from eegstream.gui.eegmonitor import EEGMonitor
from eegstream.gui.signal import SignalInterface
from eegstream.streaming import PacketReceiver, PacketTransmitter
import eegstream.devices as devices


def start_gui(packet_receiver: PacketReceiver):
    signal_interface = SignalInterface(packet_receiver, 250, window=4)
    eegmonitor = EEGMonitor(signal_interface)
    eegmonitor.start_mainloop()

if __name__ == '__main__':
    packet_transmitter, packet_receiver = \
        devices.tools.make_packet_connection(
            device=devices.OpenBCI8, filename='eegstream_openbci8_gui.fifo')

    with packet_receiver, packet_transmitter:
        gui = Process(target=start_gui, args=(packet_receiver,))
        gui.daemon = True
        print('Starting gui...')
        gui.start()
        sleep(1)
        print('Starting streaming')
        for data in np.sin(np.arange(10**5) * np.pi * 2 / 500) * np.sin(
                np.arange(10**5) * 2 * np.pi/ 25):
            sleep(0.004)
            #print(data, file=sys.stderr)
            packet_transmitter.send([data] + [0] * 7)
            if not gui.is_alive():
                break
