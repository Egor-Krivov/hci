from multiprocessing import Process

from nose import with_setup

from hci.sources.dummy import Dummy


class DummyTestController:
    @classmethod
    def start_dummy_streaming_process(cls):
        def test_streaming():
            device = Dummy()
            device.start_streaming()

        cls.process = Process(target=test_streaming)
        cls.process.start()

    @classmethod
    def stop_dummy_streaming_process(cls):
        cls.process.terminate()

def with_dummy_transmitter_setup(f):
    return with_setup(DummyTestController.start_dummy_streaming_process,
                      DummyTestController.stop_dummy_streaming_process)(f)
