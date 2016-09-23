import numpy as np
import scipy.signal as signal

from joblib import Parallel, delayed

from statsmodels.tsa.ar_model import AR

from sklearn.linear_model import LogisticRegressionCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix

sfreq = 250
nyq = sfreq / 2
epoch_len = 250
epoch_step = 50

cut_begin = 150
cut_end = 150

channel_mask = np.array([True] * 6 + [False, False])

def build_filter():
    die_window = 3
    live_window = 4
    live_gain = 2 ** 0.5

    freq_full = [0, 3, 5,
            50-live_window, 50-die_window, 50+die_window, 50+live_window,
            100-live_window, 100-die_window, 100+die_window, 100+live_window,
            nyq]

    gain_full = [0, 0, 2 ** 0.5,
            live_gain, 0, 0, live_gain,
            live_gain, 0, 0, live_gain,
            1]

    freq_low = [0, 3, 5,
               40, 45, nyq]

    gain_low = [0, 0, live_gain,
               live_gain, 0, 0]

    b = signal.firwin2(sfreq, freq_low, gain_low, nyq=nyq, antisymmetric=False)
    return b

def get_epochs(signals_raw, signal_timestamps, class_raw, class_timestamps):
    new_x, new_y = [], []
    for i in range(len(class_raw)-1):
        mask = (signal_timestamps > class_timestamps[i]) & (signal_timestamps < class_timestamps[i+1])
        temp_x = signals_raw[mask]
        # Cut beginning and an end
        new_x_vals = []
        new_y_vals = []
        for j in range(cut_begin, len(temp_x)-cut_end-epoch_len, epoch_step):
            new_x_vals.append(temp_x[j:epoch_len+j])
            new_y_vals.append(int(class_raw[i]))

        new_x.extend(new_x_vals)
        new_y.extend(new_y_vals)

    return np.array(new_x), np.array(new_y)

def load_data(name):

    data = np.genfromtxt(name+'_bci.csv', delimiter=';')
    data_y = np.genfromtxt(name+'_experiment.csv', delimiter=';')

    signal_timestamps, signals_raw = data[:, 0], data[:, 1:]
    class_timestamps, class_raw = data_y[:, 0], data_y[:, 1:]

    #signals_raw = signals_raw[]

    signals_raw = signals_raw - signals_raw.mean(axis=1, keepdims=True)
    signals_raw = signals_raw - np.mean(signals_raw, axis=0, keepdims=True)

    b = build_filter()
    signals_filtered = signal.lfilter(b, 1, signals_raw, axis=0)

    xs, ys = get_epochs(signals_filtered, signal_timestamps, class_raw,
                        class_timestamps)
    return xs, ys

def build_fe():
    def ft_augment(c):
        if not hasattr(c, 'fit_transform'):
            class augmented_class(c):
                def fit_transform(self, x, y):
                    self.fit(x, y)
                    return self.transform(x)

            return augmented_class
        else:
            return c

    @ft_augment
    class TransformerWrapper:
        def __init__(self, *transformers):
            assert len(transformers) > 0
            self.transformers = transformers

        def fit(self, x, y=None):
            pass

        def transform(self, x):
            x_t = transformers[0](x)
            for t in transformers[1:]:
                x_t = np.hstack((x_t, t(x)))
            return x_t

    def diff_abs(x):
        past_val = x[..., :-1]
        cur_val = x[..., 1:]
        diff = cur_val - past_val
        return np.abs(x).sum(axis=-1)

    def h_activity(x):
        # print(x.var(axis=-1).shape)
        return x.var(axis=-1)

    def h_mobility(x):
        x_prev = x[..., :-2]
        x_cur = x[..., 1:-1]
        x_next = x[..., 2:]

        x_diff = x_next - x_prev
        return (h_activity(x_cur * x_diff) / h_activity(x)) ** 0.5

    def h_complexity(x):
        x_prev = x[..., :-2]
        x_cur = x[..., 1:-1]
        x_next = x[..., 2:]

        x_diff = x_next - x_prev
        return h_mobility(x_cur * x_diff) / h_mobility(x)

    def zc(x):
        x_prev = x[..., :-1]
        x_next = x[..., 1:]
        zero_crossing = (x_prev * x_next) > 0
        return zero_crossing.sum(axis=-1)

    def slope_sign_change(x):
        x_prev = x[..., :-1]
        x_next = x[..., 1:]
        x_diff = x_next - x_prev
        return zc(x_diff)

    def skewness(x):
        return (((x - x.mean(axis=-1, keepdims=True)) / x.var(axis=-1,
                                                              keepdims=True) ** 0.5) ** 3).mean(
            axis=-1)

    def ar_features(x, maxlag=6):
        return np.hstack([AR(c).fit(maxlag=maxlag).params for c in x])

    def ar(x):
        x_ts = [ar_features(signal) for signal in x]
        return np.array(x_ts)

    def power(x):
        spec = []
        for epoch in x:
            f, p = signal.welch(epoch, fs=sfreq)
            spec.append(p)
        spec = np.array(spec)
        spec = spec[:, :, (f > 10) | (f < 40)]
        p = np.sum(spec, axis=-1)
        return p

    transformers = [power, diff_abs, zc, h_activity, h_mobility, h_complexity,
                    slope_sign_change, skewness, ar]
    fe = TransformerWrapper(*transformers)
    return fe

def build_clf(x, y, fe):

    n = len(x)

    x_train = x[:n * 2 // 3]
    x_val = x[n * 2// 3:]

    y_train = y[:n * 2 // 3]
    y_val = y[n * 2// 3:]

    x_train_ts = fe.fit_transform(x_train, y_train)
    x_val_ts = fe.transform(x_val)

    scaler = StandardScaler()

    x_train_ts = scaler.fit_transform(x_train_ts)
    x_val_ts = scaler.transform(x_val_ts)

    train = np.arange(len(x_train_ts))
    val = np.arange(len(x_val_ts)) + len(train)

    x = np.vstack((x_train_ts, x_val_ts))
    y = np.hstack((y_train, y_val))

    cv = ((train, val),)
    clf = LogisticRegressionCV(Cs=21, cv=cv, n_jobs=-1)
    clf.fit(x, y)
    y_pred = clf.predict(x_val_ts)

    acc = accuracy_score(y_val, y_pred)
    print('{}'.format(acc))
    print(confusion_matrix(y_val, y_pred))

    def new_clf(x):
        x_ts = scaler.transform(x)
        y_pred = clf.predict_proba(x_ts)[:, 1]
        return y_pred

    return new_clf

def build_analyser(name):
    x, y = load_data(name)
    fe = build_fe()
    clf = build_clf(x.swapaxes(1, 2), y, fe)

    b = build_filter()

    def predict(x):
        x = x - x.mean(axis=1, keepdims=True)
        x = x - np.mean(x, axis=0, keepdims=True)

        x = signal.lfilter(b, 1, x, axis=0)
        x = x[-epoch_len:]
        x = np.array([x])
        x = x.swapaxes(1, 2)
        x = fe.transform(x)
        return clf(x)[0]

    return predict

if __name__ == '__main__':
    build_analyser('artem_1')