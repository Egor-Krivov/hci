from abc import ABCMeta, abstractmethod, abstractclassmethod
from copy import deepcopy
import json


class Device(metaclass=ABCMeta):
    """Abstract class for some device. Hides default settings implementation."""
    @classmethod
    @abstractmethod
    def get_default_settings(cls):
        """Return default settings for the device."""
        pass


class JsonDevice(Device):
    """Class for device with settings in device's folder in json file."""
    @classmethod
    def get_default_settings(cls):
        with open(cls.settings_path) as f:
            settings = json.load(f)
        return settings
