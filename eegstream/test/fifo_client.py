import struct
import sys
import time

from eegstream.streaming import datalink


INTEGER_SIZE = 4  # integer size
MAX_NUM_OF_INTEGERS = 2**16 // INTEGER_SIZE  # max number of integers to receive
settings = {'datalink': {'file': 'fifo_test.fifo'}}  # settings dictionary

with datalink.FifoReceiver(settings) as fifo_r:

    while True:
        # sleep timeout
        time.sleep(5)
        # receive integers in bytes object
        b_data = fifo_r.receive(MAX_NUM_OF_INTEGERS*INTEGER_SIZE)

        # there is no data to read from the fifo
        # if b_data is None:
        #     print('empty')
        #     continue

        # calculate actual data length, can be less then max number of integers
        b_data_len = len(b_data)

        if b_data_len % (4*INTEGER_SIZE) != 0:
            print('Unexpected error with PIPE_BUF', file=sys.stderr)
            time.sleep(5)

        # unpack data from bytes object
        data = struct.unpack('i'*(b_data_len//INTEGER_SIZE), b_data)
        print(len(data), file=sys.stderr)
