import tkinter as tk

class Table:
    def setup_widgets(self, header_row, dimensions):
        if len(header_row) != dimensions[1]:
            raise Exception("header row length doesn't match dimensions in table")
        idx = 0
        for caption in header_row:
            l = tk.Label(self.frame, text=caption)
            l.grid(row=0, column=idx, sticky=tk.W)
            l.config(bg=self.bg_color)
            idx += 1
            self.headers.append(l)
        for row in range(1, dimensions[0] + 1):
            r = []
            for col in range(0, dimensions[1]):
                e = tk.Entry(self.frame, width=8, justify=tk.RIGHT)
                e.grid(row = row, column = col)
                e.config(bg = "white");
                r.append(e)
            self.cells.append(r)
        
    def __init__(self, frame, header_row, dimensions, bg_color):
        self.cells = []
        self.headers = []
        self.frame = frame
        self.bg_color = bg_color
        self.setup_widgets(header_row, dimensions)

    def get(self, row, column):
        return self.cells[row][column].get()

    def set(self, row, column, value):
        #print "set: {0}, {1}".format(row, column)
        #print "dims: {0}, {1}".format(len(self.cells), 0)
        self.cells[row][column].delete(0, tk.END)
        if isinstance(value, float):
            s = "{:10,.2f}".format(value)
        else:
            s = str(value)
        self.cells[row][column].insert(0, s)

    def set_column_width(self, column, width):
        self.headers[column].config(width=width);
        for r in self.cells:
            r[column].config(width=width);
