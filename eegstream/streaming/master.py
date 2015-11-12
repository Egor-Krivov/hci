import time

import collections
import numpy as np

SLEEP_TIMEOUT = 0.001


class Master:
    """Master class to communicate with given worker.

    Parameters
    ----------
    worker : instance of Worker
        Each acquisition device should provide specific Worker class to
        communicate with underlying data link and corresponding device daemon.
    epoch_len : int
        Number of samples to handle as complete epoch for classifier.
    step : int, optional
        Number of samples to update epoch and classifier prediction.
    mask : str | None, optional
        Indices of channels to include (if None, all channels are used).
    tofile : bool, optional
        Write aquired data to file.

    """
    def __init__(self, worker, epoch_len, step=1, mask=None, tofile=False):
        self.worker = worker
        self.epoch_len = epoch_len
        self.step = step
        self.mask = mask
        self.tofile = tofile

        # Calculate deque based buffer length in accordance with system
        # protocol and corresponding packet size.
        self.deque_len = 2**16 // worker.packet_size
        # Create empty deque based buffer for realtime aquired data. The deque
        # is bounded to the specified maximum length. Once a bounded length
        # deque is full, when new items are added, a corresponding number of
        # items are discarded from the opposite end.
        self.deque = collections.deque(maxlen=self.deque_len)

    def __enter__(self):
        self.worker.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.worker.__exit__(exc_type, exc_val, exc_tb)

    def get_epoch(self):
        """Get actual samples as epoch.

        Returns
        -------
        epoch : 2d array (n_chans, epoch_len)
            Actual samples to handle as complete epoch, aquired from device.

        """
        while True:
            # Read all samples from data link buffer.
            sample_list = self.worker.receive(self.deque_len)
            # Add aquired samples to deque.
            self._extend_deque(sample_list)

            if len(self.deque) < self.epoch_len:
                # There is not enough samples to handle as complete epoch.
                time.sleep(SLEEP_TIMEOUT)
                continue
            elif len(sample_list) < self.step:
                # Pipeline is fast enough to classify epochs in realtime. It
                # means that `t(step) > t_clf(epoch_len)` and pipeline can
                # classify epochs of length `epoch_len` faster than `step` new
                # samples can be aquired from device.
                epoch = self._get_epoch()
                # Pop out of date samples from deque.
                self._pop_deque()
                return epoch
            else:
                # Pipeline is too slow to classify epochs in realtime. It means
                # that `t(step) < t_clf(epoch_len)` and pipeline can't classify
                # each epoch of length `epoch_len` at the rate of `step` new
                # samples aquired from device. In order to overcome potential
                # deque overflow, algoritm will use only up to date samples,
                # discarding all previous aquared samples. This approach can
                # reduce classification latency, but instead produce big gaps
                # in aquired samples. Only epochs aquired directly after
                # pipeline routine will be used for prediction.
                epoch = self._get_epoch()
                # Pop out of date samples from deque.
                self._pop_deque()
                print('Slow pipeline...')
                return epoch

    def _extend_deque(self, sample_list):
        """Extend deque based buffer with new samples."""
        self.deque.extend(sample_list)

    def _pop_deque(self):
        """Remove from deque based buffer out of data samples."""
        # Only most right samples are up to date.
        offset = len(self.deque) - self.epoch_len + self.step

        for _i in range(offset):
            self.deque.popleft()

    def _get_epoch(self):
        """Return actual epoch from deque based buffer."""
        # Only most right samples are up to date.
        return np.array(self.deque)[-self.epoch_len:].T
