import sys
import os
import random
from numpy import loadtxt
import tkinter as tk
from tkinter import filedialog
#import tkFileDialog
from RawQData import RawQData
from WaterAnalyzer import WaterAnalyzer, MINIMUM_TIER_PRICE, SECOND_TIER_PRICE, LAST_TIER_PRICE, set_key_rates
from TableUI import Table
from rate_tier import TierSystem, RateTier

app_bg_color = 'gray'
#GRAPH_MAX = 2500
#GRAPH_MAX = 2200
GRAPH_MAX = 450

tier_system = None

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
    def inv_map_x(self, x):
        return x - self.top_left[0]
    def inv_map_y(self, y):
        return y - self.top_left[1]

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
    y_sampler = LinearMapping((0, GRAPH_MAX), (0, graph_rect.height()))
    x_sampler = LinearMapping((0, len(values)), (0, graph_rect.width()))
    x0 = graph_rect.map_x(0)
    xmax = graph_rect.map_x(graph_rect.width())
    y0 = graph_rect.map_y(0)
    ymax = graph_rect.map_y(graph_rect.height())
    canvas.create_line(x0, y0, x0, ymax, fill="black")
    canvas.create_line(x0, y0, xmax, y0, fill="black")
    x_step = int(graph_rect.width() / 10)
    for xin in range(0, graph_rect.width(), x_step):
        x = graph_rect.map_x(xin)
        canvas.create_line(x, y0, x, y0 + MAJOR_TICK_SIZE, fill="black")
        x_val = x_sampler.f_inverse(xin)
        canvas.create_text(x, y0 + 10, text="{0}".format(int(x_val)), anchor = tk.NW)
    #y_step = int(values[len(values) - 1] / 10)
    #for yin in xrange(0, int(values[len(values) - 1]), y_step):
    y_step = int(GRAPH_MAX / 10)
    for yin in range(0, GRAPH_MAX, y_step):
        y_val = yin
        y = graph_rect.map_y(y_sampler.f(y_val))
        canvas.create_line(x0 - MAJOR_TICK_SIZE, y, x0, y, fill="black")
        canvas.create_text(x0 - MAJOR_TICK_SIZE - AXIS_LABEL_MARGIN, y, text="{0}".format(int(y_val)), anchor = tk.NW)

def render_tier_lines(canvas, graph_rect):
    y_mapping = LinearMapping((0, GRAPH_MAX), (0, graph_rect.height()))
    for t in tier_system.get_tiers():
        y_val = y_mapping.f(t.high_bound);
        y = graph_rect.map_y(y_val);
        canvas.create_line(graph_rect.map_x(0), y, graph_rect.map_x(graph_rect.width()), y, fill="black", dash=(4,4))

blue_h = None
blue_v = None
usage_text = None
tier_text = []
total_text = None
comparison_text = None
def mouse_move(event, values, graph_rect):
    global blue_h
    global blue_v
    global usage_text
    global tier_text
    global total_text
    global comparison_text
    #print "move: {0}, {1}".format(event.x, event.y)
    x_mapping = LinearMapping((0, graph_rect.width()), (0, len(values) - 1))
    y_mapping = LinearMapping((0, GRAPH_MAX), (0, graph_rect.height()))
    x_val = graph_rect.inv_map_x(event.x)
    index = int(x_mapping.f(x_val))
    if index < len(values):
        usage = values[index]
        y_val = y_mapping.f(usage)
        x1 = graph_rect.map_x(x_val)
        y1 = graph_rect.map_y(y_val)
        x0 = graph_rect.map_x(0)
        y0 = graph_rect.map_y(0)
        if not blue_h is None:
            canvas.delete(blue_h)
        if not blue_v is None:
            canvas.delete(blue_v)
        blue_h = canvas.create_line(x0, y1, x1, y1, fill="blue")
        blue_v = canvas.create_line(x1, y0, x1, y1, fill="blue")
        
        canvas.itemconfigure(usage_text, text=str(usage))
        tier_system.clear_account()
        tier_system.account(usage)
        comparison_tiers.clear_account()
        comparison_tiers.account(usage)
        index = 0
        for t in tier_system.get_tiers():
            canvas.itemconfigure(tier_text[index], text="tier {0}: ${1:10.2f}, v={2}".format(index + 1, float(t.revenue), t.total_volume))
            index += 1
        revenue = float(tier_system.total_revenue())
        compare_revenue = float(comparison_tiers.total_revenue())
        canvas.itemconfigure(total_text, text="total: ${0:10.2f}".format(revenue))
        if compare_revenue > 0.0:
            canvas.itemconfigure(comparison_text, text="comparison: ${0:.2f} {1:.2f}%".format(compare_revenue,
                                                                                                  (revenue - compare_revenue) / compare_revenue * 100.0))
        else:
            canvas.itemconfigure(comparison_text, text="comparison: ${0:.2f}".format(compare_revenue))
            
                              
def setup_report_text(canvas):
    global usage_text
    global tier_text
    global total_text
    global comparison_text
    left = 200
    top = 25
    step = 20
    for t in tier_text:
        canvas.delete(t)
    tier_text = []
    if not usage_text is None:
        canvas.delete(usage_text)
    usage_text = canvas.create_text(left, top, anchor = tk.NW, text="", width = 200)
    top += step
    for t in tier_system.get_tiers():
        tier_text.append(canvas.create_text(left, top, anchor = tk.NW, text="", width = 200))
        top += step
    if not total_text is None:
        canvas.delete(total_text)
    total_text = canvas.create_text(left, top, anchor = tk.NW, text="", width = 200)
    top += step
    comparison_text = canvas.create_text(left, top, anchor = tk.NW, text="", width = 200)
        
def do_graph(canvas, values, xMargin, yMargin):
    #canvas_width =  800
    #canvas_height = 500
    graph_rect = ViewRect(canvas_width, canvas_height,
                              (xMargin + AXIS_LABEL_MARGIN, yMargin), (canvas_width - xMargin, canvas_height - yMargin))
    #canvas_width = canvas.winfo_width();
    #canvas_height = canvas.winfo_height();
    x_mapping = LinearMapping((0, graph_rect.width()), (0, len(values) - 1))
    #y_mapping = LinearMapping((0, values[len(values) - 1]), (0, graph_rect.height()))
    y_mapping = LinearMapping((0, GRAPH_MAX), (0, graph_rect.height()))
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
    for x_val in range(x_step, graph_rect.width(), x_step):
        x0, y0 = render_segment(x_val, x0, y0)
    x0, y0 = render_segment(graph_rect.width(), x0, y0)
    render_tier_lines(canvas, graph_rect)
    canvas.bind("<Motion>", lambda event: mouse_move(event, values, graph_rect))
    setup_report_text(canvas)

def install_comparison_tier_system(ts):
    global comparison_tiers
    comparison_tiers = ts
    comparison_tiers.clear_account()
    for q in raw_Qs.Qs:
        for v in q:
            comparison_tiers.account(v.get_billable_usage())
    comp_annual_total_revenue = comparison_tiers.total_revenue()
    comp_revenue_table.set(4, 1, comparison_tiers.total_revenue())
    row = 0
    for q in raw_Qs.Qs:
        comparison_tiers.clear_account()
        for v in q:
            comparison_tiers.account(v.get_billable_usage())
        comp_revenue_table.set(row, 1, comparison_tiers.total_revenue())
        comp_revenue_table.set(row, 2, (float(comparison_tiers.total_revenue()) / float(comp_annual_total_revenue)) * 100.0)
        row += 1

def install_tier_system(ts):
    global tier_system
    row = 0
    if not tier_system is None:
        for t in tier_system.get_tiers():
            tier_table.set(row, 0, "")
            tier_table.set(row, 1, "")
            tier_table.set(row, 2, "")
            elasticity_table.set(row, 0, "")
            row += 1
    tier_system = ts
    row = 0
    for t in ts.get_tiers():
        tier_table.set(row, 0, t.low_bound);
        tier_table.set(row, 1, t.high_bound);
        tier_table.set(row, 2, t.rate);
        elasticity_table.set(row, 0, 1.0)
        row += 1
    tier_system.clear_account()
    for q in raw_Qs.Qs:
        for v in q:
            tier_system.account(v.get_billable_usage())
    annual_total_volume = tier_system.total_volume()
    annual_total_revenue = tier_system.total_revenue()
    volume_table.set(4, 1, annual_total_volume)
    revenue_table.set(4, 1, tier_system.total_revenue())
    for t in tier_system.get_tiers():
        t.log(logger)
    row = 0
    for q in raw_Qs.Qs:
        tier_system.clear_account()
        for v in q:
            tier_system.account(v.get_billable_usage())
        volume_table.set(row, 1, tier_system.total_volume())
        volume_table.set(row, 2, (float(tier_system.total_volume()) / float(annual_total_volume)) * 100.0)
        revenue_table.set(row, 1, tier_system.total_revenue())
        revenue_table.set(row, 2, (float(tier_system.total_revenue()) / float(annual_total_revenue)) * 100.0)
        row += 1
    setup_report_text(canvas)
    select_quarter()
        
class Logger:
    def __init__(self):
        print('Logger')
    def log(self, msg):
        print(msg)

logger = Logger()


def select_quarter():
    canvas.delete("all")
    if Q_var.get() == 4:
        do_graph(canvas, account_totals, 20, 20)
    else:
        do_graph(canvas, [ x.get_usage() for x in raw_Qs.Qs[Q_var.get()] ], 20, 20)

root = tk.Tk()

top_frame = tk.Frame(root, bg=app_bg_color, width=600, height=50, pady=3)
center_frame= tk.Frame(root, bg=app_bg_color, width=50, height=50, padx = 3, pady=3)
bottom_frame= tk.Frame(root, bg=app_bg_color, width=600, height=400, pady=3)

root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)
top_frame.grid(row=0, sticky="ew")
center_frame.grid(row=1, sticky="nsew")
#pad_frame.grid(row=2, column=0)
bottom_frame.grid(row=2, column = 0, sticky="ew")

def ask_file_helper(caption, dir, ext_desc, ext):
    options = {}
    options['defaultextension'] = ext
    options['filetypes'] = [('all files', '.*'), (ext_desc, ext)]
    options['initialdir'] = dir
    options['title'] = caption
    filename = filedialog.askopenfilename(**options)
    return filename

def ask_file_save_as_helper(caption, dir, ext_desc, ext):
    options = {}
    options['defaultextension'] = ext
    options['filetypes'] = [('all files', '.*'), (ext_desc, ext)]
    options['initialdir'] = dir
    options['title'] = caption
    filename = filedialog.asksaveasfilename(**options)
    return filename

def ask_tier_file():
    options = {}
    options['defaultextension'] = '.txt'
    options['filetypes'] = [('all files', '.*'), ('text files', '.txt')]
    options['initialdir'] = os.getcwd() + '/tiers'
    options['title'] = 'Load Tier System'
    filename = filedialog.askopenfilename(**options)
    return filename

def load_tier_system():
    filename = ask_tier_file()
    if not filename == '':
        lines = loadtxt(filename)
        rates = TierSystem()
        for l in lines:
            rates.add_tier(RateTier(l[0], l[1], l[2]))
        install_tier_system(rates)
        tier_system_label.config(text=os.path.split(filename)[1])

def load_comparison_tiers(filename):
    lines = loadtxt(filename)
    rates = TierSystem()
    for l in lines:
        rates.add_tier(RateTier(l[0], l[1], l[2]))
    comparison_tiers = rates
    comparison_system_label.config(text=os.path.split(filename)[1])
    install_comparison_tier_system(rates)
    
def load_comparison_tiers_event():
    filename = ask_tier_file()
    if not filename == '':
        load_comparison_tiers(filename)

def save_graph_event():
    filename = ask_file_save_as_helper("Save graph", os.getcwd(), "EPS file", ".eps")
    if not filename == '':
        canvas.postscript(file=filename)

def analyze_current_data_set():
    global analyzer
    analyzer = WaterAnalyzer(raw_Qs, logger)
    analyzer.Analyze()
    install_tier_system(analyzer.get_tier_system())
    tier_system_label.config(text='<from analysis>')
    select_quarter()
    
def load_annual_data(data_dir):
    global raw_Qs
    raw_Qs = RawQData(data_dir)
    global account_totals
    account_totals = [ x.get_usage() for x in raw_Qs.collect_account_totals()]
    data_dir_value.config(text=os.path.split(data_dir)[1])
    analyze_current_data_set()
    
def load_annual_data_event():
    options = {}
    options['initialdir'] = os.getcwd() + '/datasets'
    options['title'] = 'Load Annual Data'
    data_dir = filedialog.askdirectory(**options)
    if not data_dir == '':
        load_annual_data(data_dir)

# helper for creating and configuring label widgets
def label_widget(frame, row, column, text, width):
    if width < 0:
        id = tk.Label(frame, text=text)
    else:
        id = tk.Label(frame, text=text, width=width, anchor=tk.W)
    id.grid(row=row, column=column, sticky=tk.W)
    id.config(bg=app_bg_color)
    return id

def button_widget(frame, row, column, text, command):
    id = tk.Button(frame, text=text, command=command)
    id.grid(row=row, column=column, sticky=tk.W)
    id.config(bg=app_bg_color)
    return id

# top frame widgets
top_frame.grid_rowconfigure(0, weight=1)
top_frame.grid_columnconfigure(1, weight=1)

label_widget(top_frame, 0, 0, 'Data set:', -1)
data_dir_value = label_widget(top_frame, 0, 1, '', 20)
label_widget(top_frame, 0, 2, 'Tier system:', -1)
tier_system_label = label_widget(top_frame, 0, 3, '', 20)
label_widget(top_frame, 0, 4, 'Comparison system:', -1)
comparison_system_label = label_widget(top_frame, 0, 5, '', 20)
button_widget(top_frame, 0, 6, 'Load data...', load_annual_data_event)
button_widget(top_frame, 0, 7, 'Load tiers...', load_tier_system)
button_widget(top_frame, 0, 8, 'Load comp tiers...', load_comparison_tiers_event)
button_widget(top_frame, 0, 9, 'Save graph...', save_graph_event)

# center frame widgets
center_frame.grid_rowconfigure(0, weight=1)
center_frame.grid_columnconfigure(1, weight=1)

Q_frame = tk.Frame(center_frame, bg=app_bg_color, width=200, height=300)
graph_frame = tk.Frame(center_frame, bg='white', width=600, height=400, pady=3, padx=3)
tier_frame = tk.Frame(center_frame, bg=app_bg_color, width=300, height=400, pady=3, padx=3)
elasticity_frame = tk.Frame(center_frame, bg=app_bg_color, width=100, height=400, pady=3, padx=3)

graph_frame.grid(row=0, column = 1, sticky='nsew')
tier_frame.grid(row=0, column = 2, sticky='ns')
elasticity_frame.grid(row=0, column = 3, sticky='ns')

# Q widgets
Q_var = tk.IntVar()
Q_var.set(0)

radio_params = [ ("Q1", 0), ("Q2", 1), ("Q3", 2), ("Q4", 3), ("Annual", 4) ]
for r in radio_params:
    rb = tk.Radiobutton(Q_frame, text=r[0], variable=Q_var, value=r[1], command=select_quarter)
    rb.grid(row=r[1], column=0, sticky=tk.W)
    rb.config(bg=app_bg_color)
Q_frame.grid(row=0, column = 0, sticky='ns')

# Set up the graph
canvas_width =  600
canvas_height = 300
canvas = tk.Canvas(graph_frame, width=canvas_width, height=canvas_height, bg='white')
canvas.grid(row=0, column=0, sticky='nsew')

# Set up the tier frame
tier_table = Table(tier_frame, ["Low", "High", "Price"], (12, 3), app_bg_color)
elasticity_table = Table(elasticity_frame, ["Elasticity"], (12, 1), app_bg_color)

# Set up the bottom frames
#bottom_frame.grid_rowconfigure(0, weight=1)
#bottom_frame.grid_columnconfigure(1, weight=1)

pad_frame = tk.Frame(bottom_frame, bg=app_bg_color, width=200, height = 400, pady=3, padx=3)
pad_frame.grid_columnconfigure(0, minsize=80)
volume_frame = tk.Frame(bottom_frame, bg=app_bg_color, width=300, height=400, pady=3, padx=3)
revenue_frame = tk.Frame(bottom_frame, bg=app_bg_color, width=300, height=400, pady=3, padx=3)
comp_revenue_frame = tk.Frame(bottom_frame, bg=app_bg_color, width=300, height=400, pady=3, padx=3)
key_rates_frame = tk.Frame(bottom_frame, bg=app_bg_color, width=300, height=400, pady=3, padx=3)
pad_frame.grid(row=0, column = 0, sticky='ns')
volume_frame.grid(row=0, column = 1, sticky='ns')
revenue_frame.grid(row=0, column = 2, sticky='ns')
comp_revenue_frame.grid(row=0, column = 3, sticky='ns')
key_rates_frame.grid(row=0, column = 4, sticky='ns')

label_widget(pad_frame, 0, 0, '', -1)
volume_table = Table(volume_frame, ["Quarter", "Volume", "Pct"], (5, 3), app_bg_color)
volume_table.set(0, 0, "Q1")
volume_table.set(1, 0, "Q2")
volume_table.set(2, 0, "Q3")
volume_table.set(3, 0, "Q4")
volume_table.set(4, 0, "Annual")
volume_table.set_column_width(1, 12)
volume_table.set_column_width(2, 12)
revenue_table = Table(revenue_frame, ["Quarter", "$", "Pct"], (5, 3), app_bg_color)
revenue_table.set(0, 0, "Q1")
revenue_table.set(1, 0, "Q2")
revenue_table.set(2, 0, "Q3")
revenue_table.set(3, 0, "Q4")
revenue_table.set(4, 0, "Annual")
revenue_table.set_column_width(1, 12)
revenue_table.set_column_width(2, 12)
comp_revenue_table = Table(comp_revenue_frame, ["Quarter", "Comparison $", "Pct"], (5, 3), app_bg_color)
comp_revenue_table.set(0, 0, "Q1")
comp_revenue_table.set(1, 0, "Q2")
comp_revenue_table.set(2, 0, "Q3")
comp_revenue_table.set(3, 0, "Q4")
comp_revenue_table.set(4, 0, "Annual")
comp_revenue_table.set_column_width(1, 12)
comp_revenue_table.set_column_width(2, 12)
key_rates_table = Table(key_rates_frame, ["Tier", "Rate($)"], (3, 2), app_bg_color)
key_rates_table.set(0, 0, "First")
key_rates_table.set(1, 0, "Second")
key_rates_table.set(2, 0, "Last")
key_rates_table.set_column_width(1, 12)
key_rates_table.set(0, 1, str(MINIMUM_TIER_PRICE))
key_rates_table.set(1, 1, str(SECOND_TIER_PRICE))
key_rates_table.set(2, 1, str(LAST_TIER_PRICE))
def set_key_rates_event():
    set_key_rates(float(key_rates_table.get(0, 1)), float(key_rates_table.get(1, 1)), float(key_rates_table.get(2, 1)))
    analyze_current_data_set()
def try_elasticity_event():
    elasticity = []
    i = len(tier_system.get_tiers()) - 1
    while i >= 0:
        elasticity.append(float(elasticity_table.get(i, 0)))
        i -= 1
    tier_system.set_elasticity(elasticity)
    annual_total_volume = 0
    annual_total_revenue = 0
    NUM_ITERS = 100
    tier_system.clear_account()
    for i in range(0, NUM_ITERS):
        for q in raw_Qs.Qs:
            for v in q:
                tier_system.account(v.get_billable_usage())
        annual_total_volume += tier_system.total_volume()
        annual_total_revenue += tier_system.total_revenue()
        tier_system.clear_account()
    volume_table.set(4, 1, annual_total_volume / NUM_ITERS)
    revenue_table.set(4, 1, annual_total_revenue / NUM_ITERS)
    
button_widget(key_rates_frame, 4, 1, 'Set key rates', set_key_rates_event)
button_widget(key_rates_frame, 5, 1, 'Try elasticity', try_elasticity_event)

# Prime the application
load_annual_data(os.getcwd() + '/datasets/2017')
install_tier_system(analyzer.get_tier_system())
load_comparison_tiers(os.getcwd() + '/tiers/mbts_2017.txt')
select_quarter();

tk.mainloop()
