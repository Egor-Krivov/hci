"""Example program to show how to read a multi-channel time series from LSL."""

from pylsl import StreamInlet, resolve_stream, resolve_streams

# first resolve an EEG stream on the lab network
print("looking for an EEG stream...")
streams = resolve_streams()

# create a new inlet to read from the stream
print(streams)
inlet = StreamInlet(streams[0])

while True:
    # get a new sample (you can also omit the timestamp part if you're not
    # interested in it)
    sample, timestamp = inlet.pull_sample()
    print(timestamp, sample)