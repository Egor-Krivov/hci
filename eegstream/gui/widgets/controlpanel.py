from tkinter import *

from eegstream.gui.signal import SignalInterface

class ControlPanel(Frame):
    def __init__(self, master, signal_interface: SignalInterface, **args):
        super().__init__(master, **args)
        master = self
        self.signal_interface = signal_interface
        Label(master, text="Control Panel").pack()

        signal_controls = Frame(master)
        signal_controls.pack(side=LEFT, expand=TRUE, fill=Y)
        Label(signal_controls, text='Signals').pack()
        self.channel = IntVar(value=0)
        for channel in range(self.signal_interface.channels):
            control_radiobutton = Radiobutton(
                signal_controls, text=str(channel+1), value=channel,
                variable=self.channel, command=self.change_mask)
            control_radiobutton.pack(expand=True, fill=BOTH)

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

    def change_mask(self):
        channel_mask = [False] * 8
        channel_mask[self.channel.get()] = True
        self.signal_interface.change_mask(channel_mask)

if __name__ == '__main__':
    root = Tk()
    class x:
        def __init__(self):
            self.channels = 8
    widget = ControlPanel(root, x())
    widget.pack(expand=TRUE, fill=BOTH)
    root.mainloop()
