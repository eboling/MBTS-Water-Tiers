import tkinter as tk
from tkinter import ttk

class Table(ttk.Frame):
    def __setup_widgets(self, header_row, dimensions, readonly):
        self.rows = dimensions[0]
        self.columns = dimensions[1]
        if len(header_row) != dimensions[1]:
            raise Exception("header row length doesn't match dimensions in table")
        for caption, col in zip(header_row, range(0, self.columns)):
            l = ttk.Label(self, text=caption)
            self.headers.append(l)
            self.columnconfigure(col, weight=1)
        for row in range(1, dimensions[0] + 1):
            r = []
            for col in range(0, dimensions[1]):
                e = ttk.Entry(self, width=8, justify=tk.RIGHT, state='readonly' if readonly else state.tk.NORMAL)
                r.append(e)
            self.cells.append(r)
            self.rowconfigure(row, weight=1)
        self.__regrid()

    def __regrid(self):
        for h in self.headers:
            h.grid_forget()
        for r in self.cells:
            for c in r:
                c.grid_forget()
        for h, col in zip(self.headers, range(0, self.columns)):
            h.grid(row=0, column=col, sticky=tk.EW)
        for r, row in zip(self.cells, range(1, self.rows + 1)):
            for c, col in zip(r, range(0, self.columns)):
                c.grid(row=row, column=col)

    def delete_rows(self, start_row, count):
        end_row = start_row + count
        for row in range(start_row, end_row):
            for cell in self.cells[row]:
                cell.grid_forget()
                cell.destroy()
        del self.cells[start_row:end_row]
        self.rows = len(self.cells)
        self.__regrid()

    def delete_columns(self, start_col, count):
        end_col = start_col + count
        for row in self.cells:
            for col in range(start_col, end_col):
                cell = row[col]
                cell.grid_forget()
                cell.destroy()
            del row[start_col:end_col]
            
        for col in range(start_col, end_col):
            self.headers[col].grid_forget()
            self.headers[col].destroy()
        del self.headers[start_col:end_col]
        
        self.columns = self.columns - (end_col - start_col)
        self.__regrid()

    def insert_rows(self, start_row, count, readonly):
        new_rows = []
        for row in range(start_row, start_row + count):
            r = []
            for col in range(0, self.columns):
                e = ttk.Entry(self, width=8, justify=tk.RIGHT, state='readonly' if readonly else state.tk.NORMAL)
                r.append(e)
            new_rows.append(r)
            self.rowconfigure(row, weight=1)
        self.cells[start_row:start_row] = new_rows
        self.rows = len(self.cells)
        self.__regrid()

    def insert_columns(self, start_col, count, readonly):
        end_col = start_col + count
        for r, row in zip(self.cells, range(0, self.rows)):
            new_cols = []
            for col in range(start_col, end_col):
                e = ttk.Entry(self, width=8, justify=tk.RIGHT, state='readonly' if readonly else state.tk.NORMAL)
                new_cols.append(e)
            r[start_col:start_col] = new_cols

        new_headers = []
        for col in range(start_col, end_col):
            l = ttk.Label(self, text='')
            new_headers.append(l)
        self.headers[start_col:start_col] = new_headers;
        self.columns = self.columns + count
        self.__regrid()

    def set_dimensions(self, rows, columns, readonly = True):
        if rows < self.rows:
            self.delete_rows(self.rows - rows, self.rows - rows)
        if columns < self.columns:
            self.delete_columns(self.columns - columns, self.columns - columns)
        if rows > self.rows:
            self.insert_rows(self.rows, rows - self.rows, readonly)
        if columns > self.columns:
            self.insert_columns(self.columns, columns - self.columns, readonly)
        
    def __init__(self, frame, header_row, dimensions, readonly=True):
        ttk.Frame.__init__(self, frame)
        self.cells = []
        self.headers = []
        self.__setup_widgets(header_row, dimensions, readonly)

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
        state = self.cells[row][column].cget('state')
        self.cells[row][column].configure(state=tk.NORMAL)
        self.cells[row][column].delete(0, tk.END)
        self.cells[row][column].insert(0, s)
        self.cells[row][column].configure(state=state)

    def set_readonly(self, row, column, readonly):
        self.cells[row][column].configure(state='readonly' if readonly else tk.NORMAL)
        
    def set_column_width(self, column, width):
        self.headers[column].config(width=width);
        for r in self.cells:
            r[column].config(width=width);
