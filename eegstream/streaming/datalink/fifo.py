import errno
import os
import sys
import time

from .datalink import DatalinkTransmitter, DatalinkReceiver


FIFO_FILE = '/tmp/fifo_eegstream'
N_ATTEMPTS = 10


class FifoTransmitter(DatalinkTransmitter):
    """Transmitter class based on the FIFO algorithm in non-blocking mode.

    Opens the FIFO file (named pipe) for writing in non-blocking mode and
    provides mechanism for data transmission through this data link. Due to
    Unix system restrictions for writing in the FIFO in non-blocking mode,
    this transmitter may establish connection only after FIFO was opened for
    reading first. Transmitter takes into account potential connection problem
    and can wait for connection establishment up to `N ATTEMPTS` seconds.
    After this period of time an exception rises.

    Parameters
    ----------
    settings : dict

    """
    def __init__(self, settings):
        # Pop data link settings.
        super().__init__(settings)
        # Unpack useful settings.
        self.file = self.settings.pop('file', FIFO_FILE)

    def __enter__(self):
        """
        Raises
        ------
        exception.FileNotFoundError :
            Raises when couldn't open the FIFO file.
        """
        for attempt in range(N_ATTEMPTS):
            try:
                # Create descriptor for the FIFO file.
                self.fifo_fd = os.open(self.file, os.O_WRONLY | os.O_NONBLOCK)
                break
            except FileNotFoundError:
                # This happens when no one has opened the FIFO for reading.
                print('Waiting for receiver...', file=sys.stderr)
                time.sleep(1)
        else:
            # After attempts delay raises the receiver not found exception.
            raise FileNotFoundError('Failed to find receiver')

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Close the FIFO file.
        os.close(self.fifo_fd)

    def send(self, b_data):
        """Send bytes in the FIFO file in non-blocking mode.

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
        exception.BrokenPipeError :
            Raises when the FIFO is broken. For example, when there is no one
            on the reading side.

        """
        try:
            # If there is room to write `len(b_data)` bytes to the FIFO, then
            # `os.write` succeeds immediately writing all `len(b_data)` bytes,
            # otherwise fails with error (exception EAGAIN or EWOULDBLOCK).
            b_data_size = os.write(self.fifo_fd, b_data)
            # If there is still room to write `len(b_data)` bytes to the FIFO,
            # but binary length is greater than the FIFO buffer size, writing
            # operation may be non-atomic. The number of bytes written may be
            # less than expected count.
            assert b_data_size == len(b_data), 'Failed to write data block'
        except BlockingIOError as ose:
            # Suppress error when the FIFO opened, but there is no room to
            # write data in the FIFO (exception EAGAIN or EWOULDBLOCK). This
            # exception raises when an operation would block on an object set
            # for non-blocking writing. Important cases: when the FIFO is full
            # or recently was full.
            if ose.errno == errno.EAGAIN or ose.errno == errno.EWOULDBLOCK:
                print('FIFO if full: {}'.format(ose), file=sys.stderr)
                b_data_size = 0
            else:
                # Something else has happened, better reraise.
                raise

        return b_data_size


class FifoReceiver(DatalinkReceiver):
    """Receiver class based on the FIFO algorithm in non-blocking mode.

    Opens the FIFO file (named pipe) for reading in non-blocking mode and
    provides mechanism for data receiving through this data link. Due to
    Unix system restrictions for writing in the FIFO in non-blocking mode,
    this receiver should open the FIFO for reading first. Receiver takes it
    into account and creates named pipe first.

    Parameters
    ----------
    settings : dict

    """
    def __init__(self, settings):
        # Pop data link settings.
        super().__init__(settings)
        # Unpack useful settings.
        self.file = self.settings.pop('file', FIFO_FILE)
        # If started getting bytes from the writing side.
        self.streaming = False

    def __enter__(self):
        """
        Raises
        ------
        exception.FileExistsError :
            Raises when couldn't create the FIFO file, because one already
            exists.
        exception.FileNotFoundError :
            Raises when couldn't open the FIFO file.

        """
        try:
            # Create the FIFO file using file name.
            os.mkfifo(self.file)
        except FileExistsError as fee:
            # The FIFO already exists, raising an error.
            print('Failed to create FIFO: {}'.format(fee), file=sys.stderr)
            raise

        try:
            # Create descriptor for the FIFO file.
            self.fifo_fd = os.open(self.file, os.O_RDONLY | os.O_NONBLOCK)
        except FileNotFoundError as fnfe:
            # Could not create descriptor for the FIFO file.
            print('Failed to open FIFO: {}'.format(fnfe), file=sys.stderr)
            raise

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Close the FIFO file.
        os.close(self.fifo_fd)
        #os.unlink(self.file)
        try:
            # Delete the FIFO file.
            os.unlink(self.file)
        except OSError as ose:
            print('Failed to delete FIFO: {}'.format(ose), file=sys.stderr)

    def receive(self, b_data_size):
        """Receive bytes from the FIFO file in non-blocking mode.

        Parameters
        ----------
        b_data_size : int
            Number of bytes to read at most.

        Returns
        -------
        b_data : bytes object

        Raises
        ------
        exception.BrokenPipeError :
            Raises when the FIFO is broken. For example, when there is no one
            on the writing side yet.

        """
        try:
            b_data = os.read(self.fifo_fd, b_data_size)
            # If there is no one on the writing side and there were streaming
            # before. Means that server was probably closed.
            # if data == bytes() and self.streaming:
        except BlockingIOError as ose:
            # Suppress error when the FIFO opened, but there is no data to read
            # from (exception EAGAIN or EWOULDBLOCK). This exception raises
            # when an operation would block on an object set for non-blocking
            # reading.
            if ose.errno == errno.EAGAIN or ose.errno == errno.EWOULDBLOCK:
                # print('FIFO is empty: {}'.format(ose), file=sys.stderr)
                b_data = bytes()
            else:
                # Something else has happened, better reraise.
                raise

        return b_data
