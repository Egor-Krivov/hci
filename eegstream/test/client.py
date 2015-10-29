import struct
import sys
import time

from eegstream.streaming import datalink


INTEGER_SIZE = 4  # integer size
MAX_NUM_OF_INTEGERS = 12  # max number of integers to receive
settings = {'data_link': {}}  # settings dictionary
flag = False

with datalink.FifoReceiver(settings) as fifo_r:

    while True:
        # sleep timeout
        time.sleep(0.1)
        # receive integers in bytes object
        b_data = fifo_r.receive(MAX_NUM_OF_INTEGERS*INTEGER_SIZE)

        # there is no data to read from the fifo
        if b_data is None:
            print('empty')
            continue

        # there is no process to open the fifo for writing
        if len(b_data) == 0 and flag:
            print('EOF', file=sys.stderr)
            break

        if len(b_data) > 0:
            flag = True

        # calculate actual data length, can be less then max number of integers
        b_data_len = len(b_data)
        # unpack data from bytes object
        data = struct.unpack('i'*(b_data_len//INTEGER_SIZE), b_data)
        print(data, file=sys.stderr)
