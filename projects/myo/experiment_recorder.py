"""Example program to show how to read a multi-channel time series from LSL."""

import sys
from pylsl import StreamInlet, resolve_byprop
import numpy as np

from eegstream.devices import Experiment, OpenBCI8


if __name__ == '__main__':
    assert len(sys.argv) > 0, 'No experiment name provided'
    filename = sys.argv[1]
    timequant = 0.100 #s

    print("looking for device stream")
    device = OpenBCI8
    bci_info = resolve_byprop('source_id', device.source_id, timeout=1)[0]
    print("Device stream discovered")
    print('Looking for GUI source')
    experiment_info = resolve_byprop('source_id', Experiment.source_id,
                                       timeout=100)[0]
    print('GUI source discovered')

    #print(experiment_info, bci_info)

    experiment_inlet = StreamInlet(experiment_info)
    bci_inlet = StreamInlet(bci_info)

    bci_results = [[], []]
    experiment_results = [[], []]

    print('Recording')
    while True:
        # get a new sample (you can also omit the timestamp part if you're not
        # interested in it)
        bci_values, bci_timestamps = bci_inlet.pull_chunk(max_samples=device.sfreq * 60 *6)
        bci_results[0].extend(bci_values)
        bci_results[1].extend(bci_timestamps)

        experiment_values, experiment_timestamps = experiment_inlet.pull_chunk()
        experiment_results[0].extend(experiment_values)
        experiment_results[1].extend(experiment_timestamps)

        if len(experiment_results[0]) > 0 and experiment_results[0][-1][0] < 0:
            break

    experiment_results = np.hstack([np.array(experiment_results[1])[:, None],
                                    experiment_results[0]])
    np.savetxt(filename+'_experiment'+'.csv', experiment_results, delimiter=';')

    bci_results = np.hstack([np.array(bci_results[1])[:, None],
                             bci_results[0]])
    np.savetxt(filename + '_bci' + '.csv', bci_results, delimiter=';')