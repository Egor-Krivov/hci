import os
import sys
from .datalink import DataLinkTransmitter, DataLinkReceiver


class PipeTransmitter(DataLinkTransmitter):
    """

    """
    def __init__(self, settings):
        self.pname = settings['datalink'].pop('pname', '/tmp/namedpipe.fifo')

    def __enter__(self):
        # try to create the fifo file
        try:
            os.mkfifo(self.pname)
        except OSError as ose:
            print('Failed to create FIFO: {}'.format(ose), file=sys.stderr)

        # open the fifo file
        self.fifo = os.fdopen(os.open(self.pname, os.O_WRONLY | os.O_NONBLOCK), 'wb')

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # exception handling here

        # if all file descriptors referring to the write end of a pipe have
        # been closed, then an attempt to read from the pipe will see
        # end-of-file (read will return 0). If all file descriptors referring
        # to the read end of a pipe have been closed, then a write will cause
        # a SIGPIPE signal to be generated for the calling process. If the
        # calling process is ignoring this signal, then write fails with the
        # error EPIPE. An application that uses pipe should use suitable close
        # calls to close unnecessary duplicate file descriptors; this ensures
        # that end-of-file and SIGPIPE/EPIPE are delivered when appropriate.

        # close fifo file
        self.fifo.close()

        # delete the fifo file
        try:
            os.unlink(self.pname)
        except OSError as ose:
            print('Failed to delete FIFO: {}'.format(ose), file=sys.stderr)

    def send(self, byte_data):
        self.fifo.write(byte_data)
        self.fifo.flush()


class PipeReceiver(DataLinkReceiver):
    """

    """
    def __init__(self, settings):
        self.pname = settings['datalink'].pop('pname', '/tmp/namedpipe.fifo')

    def __enter__(self):
        # open the fifo file
        self.fifo = os.fdopen(os.open(self.pname, os.O_RDONLY | os.O_NONBLOCK), 'rb')

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # exception handling here

        # close fifo file
        self.fifo.close()

        # delete the fifo file
        try:
            os.unlink(self.pname)
        except OSError as ose:
            print('Failed to delete FIFO: {}'.format(ose), file=sys.stderr)

    def receive(self, byte_size):
        self.fifo.read(byte_size)

