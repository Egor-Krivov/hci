import numpy as np
import scipy.signal as sig


MIN_EPOCH_LENGTH = 2


class EBAS:
    """EEG-based activation system (EBAS).

    """
    def __init__(self, thr, thr_emg, psd_mode=False):
        self.thr = thr
        self.thr_emg = thr_emg
        self.psd_mode = psd_mode

    def detect(self, x, fs):
        """Detects signal stimulus.

        Parameters
        ----------
        x : 1d array (n_ticks, )
        fs : float

        Returns
        -------
        stim : bool

        """
        x = x.astype(np.float64)

        if x.shape[-1] < (MIN_EPOCH_LENGTH * fs):
            raise ValueError('Failed to estimate stim, too short epoch length')

        # Detect signal stimulus in alpha band (Alpha activity).
        y = self._detect(x, fs, 8, 12, psd_mode=self.psd_mode)
        stim = self._cmp(y, self.thr)

        # Detect signal stimulus in beta band (EMG activity).
        y = self._detect(x, fs, 26, 30, psd_mode=self.psd_mode)
        stim_emg = self._cmp(y, self.thr_emg)

        return stim if (stim and (not stim_emg)) else False

    @staticmethod
    def _detect(x, fs, fmin, fmax, psd_mode):
        """Detects signal stimulus."""
        x = x.astype(np.float64)

        if psd_mode:
            # Estimate power spectral density.
            f, pxx = sig.welch(x, fs, nperseg=256, noverlap=(256//2))
            # Create mask.
            mask = (f > fmin) & (f < fmax)
            # Apply mask.
            pxx = pxx[:, mask]
            # Calculate stimulus.
            y = np.mean(pxx, axis=-1)
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
        return True if val > thr else False
