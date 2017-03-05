import sys
import Tkinter as tk
import tkFileDialog
from RawQData import RawQData

class ViewRect:
    def __init__(self, outer_width, outer_height, top_left, bottom_right):
        self.top_left = top_left
        self.bottom_right = bottom_right
        self.outer_width = outer_width
        self.outer_height = outer_height

    def width(self):
        return self.bottom_right[0] - self.top_left[0]
    def height(self):
        return self.bottom_right[1] - self.top_left[1]
    def offset_x(self, x):
        return self.top_left[0] + x
    def offset_y(self, y):
        return self.top_left[1] + y
    def map_x(self, x):
        return self.offset_x(x)
    def map_y(self, y):
        return self.outer_height - self.offset_y(y)

class LinearMapping:
    def __init__(self, x, x_prime):
        self.denom = float(x[1] - x[0])
        self.scale = float(x_prime[1] - x_prime[0])
        self.inverse_denom = float(x_prime[1] - x_prime[0])
        self.inverse_scale = float(x[1] - x[0])
    def f(self, x):
        return float(x) / self.denom * self.scale
    def f_inverse(self, x):
        return float(x) / self.inverse_denom * self.inverse_scale

AXIS_LABEL_MARGIN = 75
MAJOR_TICK_SIZE = 8
    
def draw_axes(canvas, values, graph_rect):
    #y_sampler = LinearMapping((0, values[len(values) - 1]), (0, graph_rect.height()))
    y_sampler = LinearMapping((0, 2500), (0, graph_rect.height()))
    x_sampler = LinearMapping((0, len(values)), (0, graph_rect.width()))
    x0 = graph_rect.map_x(0)
    xmax = graph_rect.map_x(graph_rect.width())
    y0 = graph_rect.map_y(0)
    ymax = graph_rect.map_y(graph_rect.height())
    canvas.create_line(x0, y0, x0, ymax, fill="black")
    canvas.create_line(x0, y0, xmax, y0, fill="black")
    x_step = graph_rect.width() / 10
    for xin in xrange(0, graph_rect.width(), x_step):
        x = graph_rect.map_x(xin)
        canvas.create_line(x, y0, x, y0 + MAJOR_TICK_SIZE, fill="black")
        x_val = x_sampler.f_inverse(xin)
        canvas.create_text(x, y0 + 10, text="{0}".format(int(x_val)), anchor = tk.NW)
    #y_step = int(values[len(values) - 1] / 10)
    #for yin in xrange(0, int(values[len(values) - 1]), y_step):
    y_step = int(2500 / 10)
    for yin in xrange(0, 2500, y_step):
        y_val = yin
        y = graph_rect.map_y(y_sampler.f(y_val))
        canvas.create_line(x0 - MAJOR_TICK_SIZE, y, x0, y, fill="black")
        canvas.create_text(x0 - MAJOR_TICK_SIZE - AXIS_LABEL_MARGIN, y, text="{0}".format(int(y_val)), anchor = tk.NW)

def do_graph(canvas, values, xMargin, yMargin):
    canvas_width =  800
    canvas_height = 500
    graph_rect = ViewRect(canvas_width, canvas_height,
                              (xMargin + AXIS_LABEL_MARGIN, yMargin), (canvas_width - xMargin, canvas_height - yMargin))
    #canvas_width = canvas.winfo_width();
    #canvas_height = canvas.winfo_height();
    x_mapping = LinearMapping((0, graph_rect.width()), (0, len(values) - 1))
    #y_mapping = LinearMapping((0, values[len(values) - 1]), (0, graph_rect.height()))
    y_mapping = LinearMapping((0, 2500), (0, graph_rect.height()))
    values.sort()
    draw_axes(canvas, values, graph_rect)
    x0 = graph_rect.map_x(0)
    y0 = graph_rect.map_y(0)
    x_step = 5
    def render_segment(x_val, x0, y0):
        usage = values[int(x_mapping.f(x_val))]
        y_val = y_mapping.f(usage);
        x1 = graph_rect.map_x(x_val);
        y1 = graph_rect.map_y(y_val);
        canvas.create_line(x0, y0, x1, y1, fill="black")
        return x1, y1
    for x_val in xrange(x_step, graph_rect.width(), x_step):
        x0, y0 = render_segment(x_val, x0, y0)
    x0, y0 = render_segment(graph_rect.width(), x0, y0)
        
raw_data_dir = sys.argv[1]
raw_Qs = RawQData(raw_data_dir)
account_totals = raw_Qs.collect_account_totals()

def select_quarter():
    canvas.delete("all")
    if Q_var.get() == 4:
        do_graph(canvas, account_totals, 20, 20)
    else:
        do_graph(canvas, [ x[1] for x in raw_Qs.Qs[Q_var.get()] ], 20, 20)

root = tk.Tk()

top_frame = tk.Frame(root, bg='gray', width=800, height=50, pady=3)
center_frame= tk.Frame(root, bg='gray', width=50, height=50, padx = 3, pady=3)
bottom_frame= tk.Frame(root, bg='gray', width=800, height=50, pady=3)

root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)
top_frame.grid(row=0, sticky="ew")
center_frame.grid(row=1, sticky="nsew")
bottom_frame.grid(row=2, sticky="ew")

# top frame widgets
data_dir_label = tk.Label(top_frame, text='Data Directory:')

#load_data_button = tk.Button(self.frame, 
#                         text="QUIT", fg="red",
#                         command=self.load_data)
#    self.load_data_button.grid(row = 0, column = 2)
    
#data_dir_label.grid(

center_frame.grid_rowconfigure(0, weight=1)
center_frame.grid_columnconfigure(1, weight=1)

Q_frame = tk.Frame(center_frame, bg='gray', width=200, height=300)
graph_frame = tk.Frame(center_frame, bg='white', width=600, height=400, pady=3, padx=3)

Q_frame.grid(row=0, column = 0, sticky='ns')
graph_frame.grid(row=0, column = 1, sticky='nsew')

# Q widgets
Q_var = tk.IntVar()
Q_var.set(0)

radio_params = [ ("Q1", 0), ("Q2", 1), ("Q3", 2), ("Q4", 3), ("Annual", 4) ]
for r in radio_params:
    rb = tk.Radiobutton(Q_frame, text=r[0], variable=Q_var, value=r[1], command=select_quarter)
    rb.grid(row=r[1], column=0, sticky=tk.W)
    rb.config(bg='gray')

canvas_width =  800
canvas_height = 500
canvas = tk.Canvas(graph_frame, width=canvas_width, height=canvas_height, bg='white')
canvas.grid(row=0, column=0, sticky='nsew')

canvas.create_line(0, 100, 200, 100, fill="black", dash=(4,4))
#canvas.grid(row=0, column=0, rowspan=5)
    
#  def load_data(self):
#    data_dir = tkFileDialog.askdirectory()

#raw_data_dir = sys.argv[1]
#raw_Qs = RawQData(raw_data_dir)
#account_totals = raw_Qs.collect_account_totals()

#do_graph(canvas, [ x[1] for x in raw_Qs.Qs[0] ], 20, 20)
#do_graph(canvas, account_totals, 20, 20)
select_quarter();

#root = tk.Tk()
#app = App(root)
tk.mainloop()
