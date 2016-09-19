from pylsl import StreamInfo


class Device:
    """Abstract class for a device."""
    name = None
    type = None
    n_chans = None
    sfreq = None
    source_id = None


def make_stream_info(device: Device) -> StreamInfo:
    return StreamInfo(name=device.name, type=device.type,
                      channel_count=device.n_chans, nominal_srate=device.sfreq,
                      source_id=device.source_id)