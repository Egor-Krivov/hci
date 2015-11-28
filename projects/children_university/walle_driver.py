import sys
import time

import atexit
import serial


class WALLE:
    """WALL-E robot class.

    Parameters
    ----------
    port : str
        The port to connect to.
    baud : int
        The baud of the serial connection.
    timeout : float
        Read timeout.

    """
    def __init__(self, port=None, baud=9600, timeout=None):
        # Parse parameters.
        self.port = port
        self.baud = baud
        self.timeout = timeout
        # Establish serial port.
        self.ser = serial.Serial(port=port, baudrate=baud, timeout=timeout)
        time.sleep(5)
        print('Serial established...', file=sys.stderr)
        # WALL-E robot should stay idle in initial position.
        self.ser.write(b'z')
        self._sleep()
        # Disconnects from WALL-E robot when terminated.
        atexit.register(self._disconnect)

    def move(self):
        self.ser.write(b'w')
        self._sleep()

    def stop(self):
        self.ser.write(b'z')
        self._sleep()

    def left(self):
        self.ser.write(b'a')
        self._sleep()

    def right(self):
        self.ser.write(b'd')
        self._sleep()

    @staticmethod
    def _sleep(delay=0.01):
        time.sleep(delay)

    def _disconnect(self):
        # Close serial port.
        print('Closing Serial...', file=sys.stderr)

        if self.ser.isOpen():
            self.ser.close()


if __name__ == '__main__':
    port = '/dev/ttyUSB0'  # serial port
    baud = 9600  # serial port baud rate

    # Instantiate WALL-E robot.
    walle = WALLE(port=port, baud=baud)
    print('Robot instantiated...', file=sys.stderr)

    while True:
        walle.right()
        time.sleep(3)
        walle.stop()
        walle.left()
        time.sleep(3)
        walle.stop()
