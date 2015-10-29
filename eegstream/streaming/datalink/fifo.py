import errno
import os
import sys

from .datalink import DataLinkTransmitter, DataLinkReceiver


class FifoTransmitter(DataLinkTransmitter):
    """FIFO transmitter connects only after read fd was opened.

    Parameters
    ----------
    settings : dict

    Attributes
    ----------
    fname : str
    fifo_fd : int

    """
    def __init__(self, settings):
        self.fname = settings['data_link'].pop('fname', '/tmp/fifo')

    def __enter__(self):
        # create descriptor for the fifo file
        try:
            self.fifo_fd = os.open(self.fname, os.O_WRONLY | os.O_NONBLOCK)
        except FileNotFoundError as fnfe:
            print('Failed to create FIFO (os.O_WRONLY | os.O_NONBLOCK) descriptor: {}'.format(fnfe), file=sys.stderr)
            sys.exit(0)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # close the fifo file
        os.close(self.fifo_fd)

    def send(self, b_data):
        """Send bytes in the fifo file in non-block mode.

        If there is room to write `len(b_data)` bytes to the fifo, then
        `os.write` succeeds immediately, writing all `len(b_data)` bytes,
        otherwise write fails, with errno set to EAGAIN.

        Parameters
        ----------
        b_data : bytes object

        Returns
        -------
        b_data_size : int
            number of bytes actually written

        """
        # surpress error when fifo opened, but there is no room to write data
        # in the fifo (exception EAGAIN or EWOULDBLOCK). This exception raise
        # when an operation would block on an object set for non-blocking
        # operation
        try:
            b_data_size = os.write(self.fifo_fd, b_data)
        except OSError as ose:

            if ose.errno == errno.EAGAIN or ose.errno == errno.EWOULDBLOCK:
                print('Failed to wright in FIFO: {}'.format(ose), file=sys.stderr)
                return None
            else:
                raise  # something else has happened -- better reraise

        return b_data_size


class FifoReceiver(DataLinkReceiver):
    """FIFO receiver class.

    Parameters
    ----------
    settings : dict

    Attributes
    ----------
    fname : str
    fifo_fd : int

    """
    def __init__(self, settings):
        self.fname = settings['data_link'].pop('fname', '/tmp/fifo')

    def __enter__(self):
        # try to create the fifo file
        try:
            os.mkfifo(self.fname)
        except OSError as ose:
            print('Failed to create FIFO: {}'.format(ose), file=sys.stderr)
            sys.exit(0)

        # create descriptor for the fifo file
        try:
            self.fifo_fd = os.open(self.fname, os.O_RDONLY | os.O_NONBLOCK)
        except FileNotFoundError as fnfe:
            print('Failed to create FIFO (os.O_RDONLY | os.O_NONBLOCK) descriptor: {}'.format(fnfe), file=sys.stderr)
            sys.exit(0)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # close the fifo file
        os.close(self.fifo_fd)

        # delete the fifo file
        try:
            os.unlink(self.fname)
        except OSError as ose:
            print('Failed to delete FIFO: {}'.format(ose), file=sys.stderr)

    def receive(self, b_data_size):
        """Receive bytes from the fifo file in non-block mode.

        Parameters
        ----------
        b_data_size : int
            number of bytes to read at most

        Returns
        -------
        b_data : bytes object | None

        """
        # surpress error when fifo opened, but there is no data to read from
        # the fifo (exception EAGAIN or EWOULDBLOCK). This exception raise when
        # an operation would block on an object set for non-blocking operation
        try:
            return os.read(self.fifo_fd, b_data_size)
        except OSError as ose:

            if ose.errno == errno.EAGAIN or ose.errno == errno.EWOULDBLOCK:
                return None
            else:
                raise  # something else has happened -- better reraise
