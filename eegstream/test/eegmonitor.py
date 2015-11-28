from multiprocessing import Process
from time import sleep

import numpy as np

import eegstream.devices as devices
from eegstream.gui.eegmonitor import EEGMonitor
from eegstream.streaming.signal import SignalInterface
from eegstream.streaming import PacketReceiver


def start_gui(packet_receiver: PacketReceiver):
    signal_interface = SignalInterface(packet_receiver, freq=250, window=4,
                                       channels=devices.OpenBCI8.get_channels())
    eegmonitor = EEGMonitor(signal_interface)
    eegmonitor.start_mainloop()

if __name__ == '__main__':
    packet_transmitter, packet_receiver = \
        eegstream.connections.devices.tools.make_packet_connection(
            device=devices.OpenBCI8, filename='eegstream_openbci8_gui.fifo')

    with packet_receiver, packet_transmitter:
        gui = Process(target=start_gui, args=(packet_receiver,))
        gui.daemon = True
        print('Starting gui...')
        gui.start()
        sleep(1)
        print('Starting streaming')
        sources = []
        sources.append(np.sin(np.arange(10**5) * np.pi * 2 / 500) * np.sin(
                np.arange(10**5) * 2 * np.pi/ 25))
        sources.append(np.sin(np.arange(10**5) * np.pi * 2 / 500) * np.sin(
                np.arange(10**5) * 2 * np.pi/ 20))
        sources.append(np.sin(np.arange(10**5) * np.pi * 2 / 500) * np.sin(
                np.arange(10**5) * 2 * np.pi/ 20) * np.sin(
                np.arange(10**5) * 2 * np.pi / 10))
        sources.append(np.sin(np.arange(10**5) * 2 * np.pi / 250))
        for data in np.array(sources).T:
            sleep(0.004)
            #print(data, file=sys.stderr)
            packet_transmitter.send(np.hstack((data, [0] * (8 - len(sources)))))
            if not gui.is_alive():
                break
