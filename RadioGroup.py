import tkinter as tk
from tkinter import ttk

class RadioGroup(ttk.Frame):
    def __init__(self, parent, items, on_selection_event):
        ttk.Frame.__init__(self, parent)
        self.on_selection_event = on_selection_event
        self.var = tk.IntVar()
        row = 0
        for item in items:
            rb = ttk.Radiobutton(self, text=item[0], variable=self.var, value=item[1], command=self.on_select)
            rb.grid(row=row, column=0, sticky=tk.W)
            row += 1
            self.rowconfigure(0, weight = 1)
        self.columnconfigure(0, weight = 1)
    def on_select(self):
        self.on_selection_event(self.var.get())
    def selected(self):
        return self.var.get()
