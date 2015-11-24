from multiprocessing import Queue, Process
from time import sleep
from eegstream.gui.eegmonitor import EEGMonitor
from

def start_gui(signal_source):
    eegmonitor = EEGMonitor()
    eegmonitor.start_mainloop()

def make_iterable(queue):
    def iterable():
        while True:
            val = queue.get_nowait()
            yield  val

if __name__ == '__main__':
    signal_queue = Queue()
    gui = Process(target=start_gui, args=(make_iterable(signal_queue), iter(range(
        10000))))
    gui.daemon = True
    gui.start()
    for i in range(100000):
        sleep(0.025)
        print(signal_queue.put_nowait(i))