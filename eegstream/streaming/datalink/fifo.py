import errno
import os
import sys
import time

from .datalink import DatalinkTransmitter, DatalinkReceiver


class FifoTransmitter(DatalinkTransmitter):
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
        self.fname = settings['datalink'].pop('file', '/tmp/fifo')

    def __enter__(self):
        attempts = 60
        for attempt_count in range(attempts):
            # Create descriptor for the fifo file
            try:
                self.fifo_fd = os.open(self.fname, os.O_WRONLY | os.O_NONBLOCK)
                break
            # This happens when no one has opened pipe for reading
            except FileNotFoundError:
                print('Failed to find receiver...', file=sys.stderr)
                time.sleep(1)
        else:
            raise FileNotFoundError('Failed to find receiver.')

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # close the fifo file
        os.close(self.fifo_fd)

    def send(self, b_data):
        """Send bytes in the fifo file in non-blocking mode.

        Parameters
        ----------
        b_data : bytes object

        Returns
        -------
        b_data_size : int
            Number of bytes actually written. Can be zero, if nothing is
            written.

        Raises
        ------
        exception.BrokenPipeError
            Raises when pipe is broken. For example, when there is no one on
            the reading side

        """
        # Suppress error when fifo opened, but there is no room to write data
        # in the fifo (exception EAGAIN or EWOULDBLOCK). This exception raises
        # when an operation would block on an object set for non-blocking
        # operation. Cases: when pipe is full or recently was full (see module
        # documentation).
        try:
            # If there is room to write `len(b_data)` bytes to the fifo, then
            # `os.write` succeeds immediately, writing all `len(b_data)` bytes,
            # otherwise write fails, with errno set to EAGAIN.
            b_data_size = os.write(self.fifo_fd, b_data)
            assert b_data_size == len(b_data), 'FIFO managed to write part' \
                                               ' of information'
        except BlockingIOError as ose:
            if ose.errno == errno.EAGAIN or ose.errno == errno.EWOULDBLOCK:
                print('Failed to write to FIFO: {}, probably pipe if full'.
                      format(ose), file=sys.stderr)
                b_data_size = 0
            else:
                raise  # something else has happened -- better reraise

        return b_data_size


class FifoReceiver(DatalinkReceiver):
    """FIFO receiver class.

    Parameters
    ----------
    settings : dict

    """
    def __init__(self, settings):
        self.fname = settings['datalink'].pop('file', '/tmp/fifo')
        # If started getting bytes from the writing side
        self.streaming = False

    def __enter__(self):
        """
        Raises
        ------
        FileExistsError :
            Raises when couldn't create the fifo file, because one already
            exists.

        FileNotFoundError:
            Raises when couldn't open fifo file.

        """
        # Create the fifo file
        try:
            os.mkfifo(self.fname)
        except FileExistsError as fee:
            print('Failed to create FIFO: {}'.format(fee), file=sys.stderr)
            raise

        # Create descriptor for the fifo file
        try:
            self.fifo_fd = os.open(self.fname, os.O_RDONLY | os.O_NONBLOCK)
        except FileNotFoundError as fnfe:
            print('Failed to open FIFO: {}'.format(fnfe), file=sys.stderr)
            raise

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
        """Receive bytes from the fifo file in non-blocking mode.

        Parameters
        ----------
        b_data_size : int
            number of bytes to read at most

        Returns
        -------
        b_data : bytes object | None

        """
        # suppress error when fifo opened, but there is no data to read from
        # the fifo (exception EAGAIN or EWOULDBLOCK). This exception raise when
        # an operation would block on an object set for non-blocking operation
        try:
            data = os.read(self.fifo_fd, b_data_size)
            # If there is no one on the writing side and were streaming before,
            # meaning that server was probably closed.
            # if data == bytes() and self.streaming:
        except BlockingIOError as ose:
            if ose.errno == errno.EAGAIN or ose.errno == errno.EWOULDBLOCK:
                print('Failed to read from FIFO: {}, no data was sent yet'.
                      format(ose), file=sys.stderr)
                data = bytes()
            else:
                raise
        return data
