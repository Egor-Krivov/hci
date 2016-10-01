import tkinter as tk

def start_widget(root2widget):
    root = tk.Tk()
    widget = root2widget(root)
    widget.pack(expand=True, fill=tk.BOTH)
    root.mainloop()