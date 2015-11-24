import collections

import numpy as np
import scipy.signal as sig


MIN_EPOCH_LENGTH = 2


class AlphaDetector:
    """Alpha detector.

    Parameters
    ----------
    fs : float
    thr : float
    thr_emg : float
    psd_mode : bool, optional
    verbose : bool, optional

    """
    def __init__(self, fs, thr, thr_emg, psd_mode=True, verbose=False):
        self.fs = fs
        self.thr = thr
        self.thr_emg = thr_emg
        self.psd_mode = psd_mode
        self.verbose = verbose

    def detect(self, x):
        """Detects signal stimulus.

        Parameters
        ----------
        x : 1d array (n_ticks, )

        Returns
        -------
        y : bool

        """
        x = x.astype(np.float64)

        if x.shape[-1] < (MIN_EPOCH_LENGTH * self.fs):
            raise ValueError('Failed to estimate stim, too short epoch length')

        # Detect signal stimulus in alpha band (Alpha activity).
        stim = self._detect(x, self.fs, 8, 12, psd_mode=self.psd_mode)
        y = self._cmp(stim, self.thr)

        # Detect signal stimulus in beta band (EMG activity).
        stim_emg = self._detect(x, self.fs, 26, 30, psd_mode=self.psd_mode)
        y_emg = self._cmp(stim_emg, self.thr_emg)

        # Calculate output stimulus.
        y = y if (y and (not y_emg)) else False

        if not self.verbose:
            return y
        else:
            return y, stim, stim_emg

    @staticmethod
    def _detect(x, fs, fmin, fmax, psd_mode):
        """Detects signal stimulus."""
        x = x.astype(np.float64)

        if psd_mode:
            # Estimate power spectral density.
            f, pxx = sig.welch(x, fs, nperseg=256, noverlap=(256//2))
            # Create mask.
            mask = (f > fmin) & (f < fmax)
            # Calculate stimulus.
            y = np.mean(pxx[mask], axis=-1)
        else:
            # Design digital Butterworth filter in sos format.
            order, freq_nqst = 6, fs//2
            sos = sig.butter(order, [fmin/freq_nqst, fmax/freq_nqst],
                             btype='bandpass', analog=False, output='sos')
            # Filter signal.
            xf = sig.sosfilt(sos, x, axis=-1)
            # Calculate stimulus.
            y = np.mean(xf, axis=-1)

        return y

    @staticmethod
    def _cmp(val, thr):
        """Compares two values."""
        return True if (val > thr) else False


class EBAS:
    """EEG-based activation system (EBAS).

    """
    def __init__(self, detector, deque_len=1):
        self.detector = detector
        self.deque = collections.deque(maxlen=deque_len)

    def detect(self, x):
        """Detects signal stimulus.

        Parameters
        ----------
        x : 1d array (n_ticks, )

        Returns
        -------
        y : bool

        """
        x = x.astype(np.float64)

        # Estimate stimulus.
        y = self.detector.detect(x)[0]
        # Update deque with stimulus.
        self._update_deque(y)
        # Calculate generalized stimulus.
        y = self._detect()

        return y

    def _update_deque(self, y):
        """Updates history."""
        self.deque.append(y)

    def _detect(self):
        """Calculates generalized stimulus."""
        # Calculate deque length.
        deque_len = len(self.deque)
        # Calculate weights.
        w = np.linspace(0.25, 1.0, num=deque_len, endpoint=True)
        w /= np.sum(w)

        if np.dot(np.array(self.deque), w) > 0.5:
            return True
        else:
            return False
