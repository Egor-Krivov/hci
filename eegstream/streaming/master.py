import sys
import time
from collections import deque

import numpy as np

from eegstream.streaming import PacketReceiver
from eegstream.devices import Device


SLEEP_TIMEOUT = 0.001


class Master:
    """Master class to communicate with given worker.

    Parameters
    ----------
    packet_receiver : PacketReceiver
        Packet receiver, prepared for data transmission.
    device : Device
        Device for the data transmission.
    window : float
        Epoch length in seconds.
    mask : iterable
        Iterable with booleans, describing channels' mask. Use all channels
        as default state.
    step : int, optional
        Minimum number of samples to update epoch.
    block_mode : bool
        If methods can block to get required amount of data. If false,
        can return None instead of data.
    verbose : bool, optional
        Verbosity level.


    """

    def __init__(self, packet_receiver: PacketReceiver, device: Device,
                 window: float, mask=None, step: int=0, block_mode: bool=True,
                 verbose: bool=False):

        self.packet_receiver = packet_receiver
        self.device = device
        self.epoch_len = int(device.freq * window)
        assert self.epoch_len > 0
        self.step = step
        self.mask = [True] * device.channels if mask is None else mask
        self.mask = np.array(self.mask, dtype=bool)
        self.block_mode = block_mode
        self.verbose = verbose
        # Create empty deque based buffer for real-time acquired data. The
        # deque is bounded to the specified maximum length. Once a bounded
        # length deque is full, when new items are added, a corresponding
        # number of items are discarded from the opposite end. Deque based
        # buffer only designed to retain `epoch_len` up to date samples, all
        # other samples are discarded.
        self.deque = deque(maxlen=self.epoch_len)

    def get_epoch(self) -> np.array:
        """Get actual samples as epoch.

        Returns
        -------
        epoch : 2d array (n_chans, epoch_len)
            Actual samples to handle as a complete epoch, acquired from the
            device. Can block if block mode set to true to get enough amount
            of data. If block_mode set to False, can return None if not enough
            data was acquired yet.

        """
        while True:
            sample_list = self.packet_receiver.receive_all()
            # Add acquired samples to deque. Deque based buffer retains only
            # the last `epoch_len` samples from provided sample list. All
            # other samples are discarded, because they are out of date.
            self.deque.extend(sample_list)

            if len(self.deque) < self.epoch_len:
                if self.block_mode:
                    # There is not enough samples to handle as complete epoch.
                    time.sleep(SLEEP_TIMEOUT)
                    continue
                else:
                    return None
            else:
                # We have enough samples.
                epoch = np.array(self.deque).T
                # Pop out of date samples from deque.
                self._pop_deque()

                if len(sample_list) < self.step:
                    # Pipeline is fast enough to classify epochs in real-time.
                    # It means that `t(step) > t_clf(epoch_len)` and pipeline
                    # can classify epochs of length `epoch_len` faster than
                    # `step` new samples can be acquired from the device.
                    pass
                else:
                    # Pipeline is too slow to classify epochs in real-time. It
                    # means that `t(step) < t_clf(epoch_len)` and pipeline
                    # can't classify each epoch of length `epoch_len` at the
                    # rate of `step` new samples acquired from device. In order
                    # to overcome potential deque overflow, algorithm will use
                    # only up to date samples, discarding all previously
                    # acquired samples. This approach can reduce classification
                    # lag, but instead produces time gaps between acquired
                    # samples. Only epochs acquired directly after pipeline
                    # routine will be used for prediction.
                    if self.verbose:
                        print('Slow pipeline...', file=sys.stderr)

                return epoch[self.mask]

    def _pop_deque(self):
        """Remove from deque based buffer out of data samples."""
        for _ in range(self.step):
            self.deque.popleft()

    def __iter__(self):
        while True:
            yield self.get_epoch()
