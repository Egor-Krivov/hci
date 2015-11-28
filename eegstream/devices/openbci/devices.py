from ..device import Device


class OpenBCI8(Device):
    """OpenBCI board with 8 channels."""
    default_settings = {
        "packet": {
            "format": "8d",
            "datalink_type": "pipe"
        },
        "datalink": {
            "file": "/tmp/fifo_eegstream_openbci8"
        }
    }
    channels = 8
    freq = 250


class OpenBCI16(Device):
    """OpenBCI board with 16 channels."""
    default_settings = {
        "packet": {
            "format": "16d",
            "datalink_type": "pipe"
        },
        "datalink": {
            "file": "/tmp/fifo_eegstream_openbci16"
        }
    }
    channels = 16
    freq = 125
