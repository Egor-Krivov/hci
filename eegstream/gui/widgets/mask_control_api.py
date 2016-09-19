from tkinter import *

from eegstream.streaming.signal import MaskController

class MaskControllerAPI(Frame):
    def __init__(self, master, mask_controller: MaskController, **args):
        super().__init__(master, **args)
        self.mask_controller = mask_controller
        Label(self, text="Control Panel").pack()

        signal_controls = Frame(self)
        signal_controls.pack(side=LEFT, expand=TRUE, fill=Y)
        Label(signal_controls, text='Signals').pack()
        self.mask_variables = []
        for channel in range(self.mask_controller.n_chans):
            var = IntVar()
            control_radiobutton = Checkbutton(
                signal_controls, text=str(channel+1),
                variable=var, command=self.change_mask)
            control_radiobutton.pack(expand=True, fill=BOTH)
            self.mask_variables.append(var)

    def change_mask(self):
        channel_mask = [var.get() > 0 for var in self.mask_variables]
        self.mask_controller.mask = channel_mask

if __name__ == '__main__':
    root = Tk()
    widget = MaskControllerAPI(root, MaskController(4))
    widget.pack(expand=TRUE, fill=BOTH)
    root.mainloop()
