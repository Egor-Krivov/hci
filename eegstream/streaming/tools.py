from eegstream.devices import Device
from eegstream.streaming import PacketTransmitter, PacketReceiver


def _make_packet_transmitter(device: Device, filename: str=None):
    settings = device.default_settings
    if filename:
        settings['datalink']['file'] = filename
    return PacketTransmitter(settings)


def _make_packet_receiver(device: Device, filename: str=None):
    settings = device.default_settings
    if filename:
        settings['datalink']['file'] = filename
    return PacketReceiver(settings)


def make_packet_connection(device: Device, filename: str=None):
    receiver = _make_packet_receiver(device, filename)
    transmitter = _make_packet_transmitter(device, filename)
    return transmitter, receiver
