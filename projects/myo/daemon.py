from pylsl import StreamOutlet, StreamInfo

from eegstream.devices.openbci.daemon import start_streaming
from eegstream.devices import make_stream_info, OpenBCI8

if __name__ == '__main__':
    stream_info = make_stream_info(OpenBCI8)
    stream_outlet = StreamOutlet(stream_info)
    start_streaming(stream_outlet, port_id=0)