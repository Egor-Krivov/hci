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
    to_file : bool, optional
        Write acquired data to a file.

    """

    def __init__(self, worker, epoch_len, step=1, mask=None, to_file=False):
        self.worker = worker
        self.epoch_len = epoch_len
        self.step = step
        self.mask = mask
        self.to_file = to_file

        # Create empty deque based buffer for real-time acquired data. The
        # deque is bounded to the specified maximum length. Once a bounded
        # length deque is full, when new items are added, a corresponding
        # number of items are discarded from the opposite end. Deque based
        # buffer only designed to retain `epoch_len` up to date samples, all
        # other samples are discarded.
        self.deque = collections.deque(maxlen=self.epoch_len)

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
            Actual samples to handle as a complete epoch, acquired from the
            device.

        """
        while True:
            # Read all samples from data link.
            sample_list = self.worker.receive_all()
            # Add acquired samples to deque. Deque based buffer retains only
            # the last `epoch_len` samples from provided sample list. All
            # other samples are discarded, because they are out of date.
            self._extend_deque(sample_list)

            if len(self.deque) < self.epoch_len:
                # There is not enough samples to handle as complete epoch.
                time.sleep(SLEEP_TIMEOUT)
                continue
            else:
                # We have enough samples
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
                    # latency, but instead produces time gaps between acquired
                    # samples. Only epochs acquired directly after pipeline
                    # routine will be used for prediction.
                    print('Slow pipeline...')

                return epoch

    def _extend_deque(self, sample_list):
        """Extend deque based buffer with up to date samples."""
        self.deque.extend(sample_list)

    def _pop_deque(self):
        """Remove from deque based buffer out of data samples."""
        for _i in range(self.step):
            self.deque.popleft()
