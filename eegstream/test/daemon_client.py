import time

from eegstream.devices import OpenBCIWorker


INTEGER_SIZE = 8  # integer size
MAX_NUM_OF_INTEGERS = 2**16 // INTEGER_SIZE  # max number of integer to receive


with OpenBCIWorker() as packet_r:

    while True:
        time.sleep(2)
        data = packet_r.receive(MAX_NUM_OF_INTEGERS//8)
        print(len(data))
