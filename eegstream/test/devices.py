from eegstream.devices import OpenBCI8, OpenBCI16

print(OpenBCI8().get_default_settings())
print(OpenBCI16().get_default_settings())