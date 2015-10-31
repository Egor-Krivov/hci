from os.path import dirname, join
import json


def grab_docs_from(other_func):
    def dec(func):
        if func.__doc__:
            func.__doc__ = func.__doc__ + "\n\n    " + other_func.__doc__
        else:
            func.__doc__ = other_func.__doc__
        return func
    return dec


def load_settings(device_path):
    with open(join(device_path, 'settings.json')) as settings_file:
        settings = json.load(settings_file)
    return settings
