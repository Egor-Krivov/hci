from pylsl import StreamInfo, StreamInlet, StreamOutlet, resolve_byprop
from pylsl import FOREVER
from abc import abstractmethod, ABCMeta

import warnings

class Source:
    """Abstract class for a data source."""
    def __init__(self, *, name, type, n_chans, sfreq, source_id):

        self.name = name
        self.type = type
        self.n_chans = n_chans
        self.sfreq = sfreq
        self.source_id = source_id

    @abstractmethod
    def start_streaming(self):
        """Source starts streaming data"""
        pass

    def get_stream_inlet(self, timeout=FOREVER) -> StreamInlet:
        return source2stream_inlet(self, timeout=timeout)

    def get_stream_info(self) -> StreamInfo:
        return source2stream_info(self)

    def get_stream_outlet(self) -> StreamOutlet:
        return source2stream_outlet(self)


def source2stream_info(source: Source) -> StreamInfo:
    return StreamInfo(name=source.name, type=source.type,
                      channel_count=source.n_chans, nominal_srate=source.sfreq,
                      source_id=source.source_id)


def source2stream_inlet(source: Source, timeout=FOREVER) -> StreamInfo:
    streams_info =  resolve_byprop('source_id', source.source_id,
                                   timeout=timeout)
    if len(streams_info) == 1:
        stream_info = streams_info[0]
        return StreamInlet(stream_info)

    elif len(streams_info) > 1:
        raise ConnectionError(
            'More than one source found for {}'.format(source.source_id))

    else:
        raise ConnectionError(
            'No source {} found for receiving'.format(source.source_id))


def source2stream_outlet(source: Source) -> StreamOutlet:
    stream_info = source2stream_info(source)
    stream_outlet = StreamOutlet(stream_info)
    return stream_outlet