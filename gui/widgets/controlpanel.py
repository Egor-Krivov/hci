from tkinter import *


class ControlPanel(Frame):
    def __init__(self, master, **args):
        super().__init__(master, **args)
        master = self
        Label(master, text="Control Panel").pack()

        threshold_frame = Frame(master)
        threshold_frame.pack(side=LEFT, expand=TRUE, fill=BOTH)
        threshold = Scale(threshold_frame, from_=0, to=100,
                          orient=HORIZONTAL, label='threshold')
        threshold.pack(expand=TRUE, fill=BOTH, side=LEFT)

        lowpass_frame = Frame(master)
        lowpass_frame.pack(side=LEFT, expand=TRUE, fill=BOTH)
        lowpass = Scale(lowpass_frame, from_=0, to=100,
                        orient=HORIZONTAL, label='lowpass')
        lowpass.pack(expand=TRUE, fill=BOTH, side=LEFT)


if __name__ == '__main__':
    root = Tk()
    widget = ControlPanel(root)
    widget.pack(expand=TRUE, fill=BOTH)
    root.mainloop()
