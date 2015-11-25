from os.path import join, dirname

from ..device import JsonDevice


class OpenBCI8(JsonDevice):
    settings_name = 'openbci8_settings.json'
    settings_path = join(dirname(__file__), settings_name)


class OpenBCI16(JsonDevice):
    settings_name = 'openbci16_settings.json'
    settings_path = join(dirname(__file__), settings_name)
