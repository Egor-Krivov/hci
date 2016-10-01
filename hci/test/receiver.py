"""Example program to show how to read a multi-channel time series from LSL."""

from pylsl import StreamInlet, resolve_byprop

from hci.sources import Dummy

import time
# first resolve an EEG stream on the lab network
print("looking for an EEG stream...")

#source_id = Experiment.source_id
#stream = resolve_byprop('source_id', source_id, timeout=1)[0]

# create a new inlet to read from the stream
#print(stream)
dummy = Dummy()
inlet = dummy.get_stream_inlet()

while True:
    # get a new sample (you can also omit the timestamp part if you're not
    # interested in it)
    time.sleep(1)
    sample, timestamp = inlet.pull_chunk()
    print(len(timestamp))