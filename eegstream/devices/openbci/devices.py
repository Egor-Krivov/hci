from os.path import join, dirname

from ..device import JsonDevice


class OpenBCI8(JsonDevice):
    def __init__(self):
        settings_name = 'openbci8_settings.json'
        settings_path = join(dirname(__file__), settings_name)
        super().__init__(settings_path)


class OpenBCI16(JsonDevice):
    def __init__(self):
        settings_name = 'openbci16_settings.json'
        settings_path = join(dirname(__file__), settings_name)
        super().__init__(settings_path)