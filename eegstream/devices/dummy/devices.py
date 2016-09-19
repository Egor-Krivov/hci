from ..device import Device


class Dummy(Device):
    name = 'Dummy'
    type = ''
    n_chans = 4
    sfreq = 500
    source_id = 'Dummy'
