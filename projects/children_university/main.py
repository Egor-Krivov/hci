from multiprocessing import Process
from time import sleep

from eegstream.devices import Device, OpenBCI8
from eegstream.streaming import make_packet_connection
from eegstream.streaming import PacketReceiver, PacketTransmitter
from server_walle import start_walle_streaming

from eegstream.streaming import Master


if __name__ == '__main__':
    packet_transmitter, packet_receiver = make_packet_connection(
            device=OpenBCI8, filename='eegstream_openbci8_alpha.fifo')

    with packet_receiver, packet_transmitter:
        print('Connection activated')
        # Data streaming
        data_source_port = 0
        data_streaming = Process(target=start_walle_streaming,
                                 args=([packet_transmitter], data_source_port))
        print(data_streaming.daemon)
        print('Starting data streaming...')
        data_streaming.start()

        # Data processing
        master = Master(packet_receiver, OpenBCI8, 2, step=10, verbose=True)
        for data in master:
            print(data.mean(), data.shape[1])
