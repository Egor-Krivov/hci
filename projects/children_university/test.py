from multiprocessing import Process
from time import sleep


class Exe:
    def __init__(self, id):
        self.id = id

    def __enter__(self):
        print('enter', self.id)

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('exit', self.id)


def do_things(e1: Exe):
    e2 = Exe(1)
    with e2:
        while True:
            pass


if __name__ == '__main__':

    e1 = Exe(0)
    e3 = Exe(2)
    with e1:
        process = Process(target=do_things, args=(e1,))
        process.daemon = True
        process.start()

        with e3:
            while True:
                pass
