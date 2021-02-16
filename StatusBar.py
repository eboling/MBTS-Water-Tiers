import tkinter as tk
from tkinter import ttk

class StatusBar(ttk.Frame):
    # sections = (caption, width, section_name)
    def __init__(self, parent, sections):
        ttk.Frame.__init__(self, parent)
        column = 0
        for section in sections:
            frame = ttk.Frame(self)
            label = ttk.Label(frame, text=section[0])
            label.grid(row=0, column=0, sticky=tk.W)
#            entry = ttk.Entry(frame, width=section[1], textvariable=section[2], state='readonly')#, relief=ttk.SUNKEN)
            entry = ttk.Entry(frame, width=section[1], textvariable=section[2], state='disabled')#, relief=ttk.SUNKEN)
            entry.grid(row=0, column=1, sticky=tk.EW)
            frame.grid(row=0, column=column, sticky=tk.NSEW)
            column += 1

    def set_section(self, section_name, value):
        self.entries[section_name].configure(state='normal')
        self.entries[section_name].delete(0, 'end')
        self.entries[section_name].insert(0, value)
        self.entries[section_name].configure(state='readonly')
