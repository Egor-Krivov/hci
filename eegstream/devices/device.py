from abc import ABCMeta, abstractmethod
import json


class Device(metaclass=ABCMeta):
    """Abstract class for some device. Hides default settings implementation."""
    @abstractmethod
    def get_default_settings(self):
        """Return default settings for the device."""
        pass


class JsonDevice(Device):
    """Class for device with settings in device's folder in json file."""
    def __init__(self, settings_path):
        with open(settings_path) as f:
            self.settings = json.load(f)

    def get_default_settings(self):
        return self.settings
