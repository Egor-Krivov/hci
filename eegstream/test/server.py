import struct
import sys
import time

import numpy as np

from eegstream.streaming import datalink


INTEGER_SIZE = 4  # integer size
MAX_NUM_OF_INTEGERS = 12  # max number of integers to receive
settings = {'data_link': {}}  # settings dictionary


def gen_data(low=10, high=100, size=4):
    """Simple generator.

    """
    idx = low

    while True:
        # calculate data and corresponding data format
        data_, fmt_ = np.arange(idx, idx + size) % high, 'i'*size
        # yield data and corresponding data format
        yield data_, fmt_
        # update generator
        idx = idx + size if idx < (high - size - 2) else low


with datalink.FifoTransmitter(settings) as fifo_t:

    for data, fmt in gen_data():
        # sleep timeout
        time.sleep(0.001)
        # pack data to bytes object
        b_data = struct.pack(fmt, *(data.tolist()))
        # send bytes object
        b_data_size = fifo_t.send(b_data)

        if b_data_size == 0:
            continue

        # number of bytes actually written
        if b_data_size > 0:

            # write of less than PIPE_BUF bytes must be atomic: the output data
            # is written to the fifo as a contiguous sequence. Writes of more
            # than PIPE_BUF bytes may be nonatomic: the kernel may interleave
            # the data with data written by other processes
            if b_data_size % (4*INTEGER_SIZE) == 0:
                print(struct.unpack(fmt, b_data), file=sys.stderr)
            else:
                print('Unexpected error with PIPE_BUF', file=sys.stderr)
                time.sleep(1)
