from multiprocessing import Process
from time import sleep

import eegstream.devices as devices
from eegstream.gui.eegmonitor import EEGMonitor
from eegstream.streaming.signal import SignalInterface
from eegstream.streaming import PacketReceiver
from eegstream.devices.openbci.daemon import start_streaming


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
        streaming = Process(target=start_streaming,
                            args=([packet_transmitter],))
        streaming.daemon = True
        streaming.start()
        while True:
            sleep(1)
            if not gui.is_alive():
                break
