from multiprocessing import Process
from time import sleep

import numpy as np

from eegstream.gui.eegmonitor import EEGMonitor
from eegstream.streaming import PacketReceiver, PacketTransmitter
from eegstream.streaming.master import MAX_BUFFER, Master
import scipy.signal as sig
import eegstream.devices as devices


def start_gui(signal_receiver: PacketReceiver,
              spectrogram_receiver: PacketReceiver):
    def signal_source():
        while True:
            yield signal_receiver.receive(MAX_BUFFER)

    master = Master(spectrogram_receiver, 500, 1)

    def spectrogram_source():
        while True:
            data = master.get_epoch()
            print(data.shape)
            data = data[0]
            print(data)
            f, pxx = sig.welch(data, 250, nperseg=256, noverlap=(256//2))
            yield f, pxx
    sleep(2)
    with signal_receiver, master:
        eegmonitor = EEGMonitor(signal_source, spectrogram_source)
        eegmonitor.start_mainloop()

if __name__ == '__main__':
    signal_transmitter, signal_receiver = \
        devices.tools.make_packet_connection(
            device=devices.OpenBCI8, filename='eegstream_openbci8_signal.fifo')

    spectrogram_transmitter, spectrogram_receiver = \
        devices.tools.make_packet_connection(
            device=devices.OpenBCI8,
            filename='eegstream_openbci8_spectrogram.fifo')

    gui = Process(target=start_gui,
                  args=(signal_receiver, spectrogram_receiv er))
    gui.daemon = True
    print('Starting gui...')
    gui.start()
    sleep(2)
    print('Starting streaming')

    with signal_transmitter, spectrogram_transmitter:
        for data in np.sin(np.arange(10**5) * np.pi * 2/ 250) * np.sin(
                np.arange(10**5) * 2* np.pi/ 25):
            sleep(0.004)
            #print(data, file=sys.stderr)
            signal_transmitter.send([data] + [0] * 7)
            spectrogram_transmitter.send([data] + [0] * 7)
