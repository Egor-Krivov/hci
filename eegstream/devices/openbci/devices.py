from ..device import Device

class OpenBCI8(Device):
    """OpenBCI board with 8 channels."""
    name = 'OpenBCI8'
    type = ''
    n_chans = 8
    sfreq = 250
    source_id = 'OpenBCI8'

class OpenBCI16(Device):
    """OpenBCI board with 16 channels."""
    name = 'OpenBCI16'
    type = ''
    n_chans = 16
    sfreq = 125
    source_id = 'OpenBCI16'
