from ..device import Device
from pylsl import IRREGULAR_RATE


class Experiment(Device):
    name = 'Experiment'
    type = ''
    n_chans = 1
    sfreq = IRREGULAR_RATE
    source_id = 'Experiment'
