import tkinter as tk
from tkinter import ttk

import tier_widget
from TableUI import Table
from TableUI import DollarFormat
from TableUI import PercentageFormat
import data_bindings as DB
import water_utils as WU
from AccountingSummary import AccountingSummary

class BoundFrame(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self._bindings = DB.DataBindings()

    def update_bindings(self):
        self._bindings.push()

class SummaryTable(BoundFrame):
    def __init__(self, parent, summary, caption=None, include_q_column=True):
        BoundFrame.__init__(self, parent)
        self.summary = summary
        
        frame = self
        if caption:
            frame = ttk.LabelFrame(self, text=caption)
            frame.grid(row=0, column=0)
            
        self.include_q_column = include_q_column
        headers = ['Volume', 'Volume %', 'Revenue ($)', 'Revenue %']
        if include_q_column:
            headers = ['Quarter'] + headers
        self.table = Table(frame, headers, (5, 5 if include_q_column else 4))
        self.table.grid(row=0, column=0)
        if include_q_column:
            self.table.set(0, 0, 'Q1')
            self.table.set(1, 0, 'Q2')
            self.table.set(2, 0, 'Q3')
            self.table.set(3, 0, 'Q4')
            self.table.set(4, 0, 'Annual')
            
        base_column = 1 if include_q_column else 0
        
        self._bindings.add_binding(DB.Facet(self.summary, 'annual_volume'), self.table.binding(4, base_column), DB.FloatToInt)
        self._bindings.add_binding(DB.Facet(self.summary, 'annual_revenue'), self.table.binding(4, base_column + 2))
        for q_num in range(0, 4):
            self._bindings.add_binding(DB.Facet(self.summary.quarterly_information[q_num], 'volume'),
                                           self.table.binding(q_num, base_column), DB.FloatToInt)
            binding = DB.Binding(lambda q_num=q_num: self.summary.percentages(q_num)[0])
            self._bindings.add_binding(binding,
                                           self.table.binding(q_num, base_column + 1))
            self._bindings.add_binding(DB.Facet(self.summary.quarterly_information[q_num], 'revenue'),
                                           self.table.binding(q_num, base_column + 2))
            binding = DB.Binding(lambda q_num=q_num: self.summary.percentages(q_num)[1])
            self._bindings.add_binding(binding,
                                           self.table.binding(q_num, base_column + 3))
        self.table.format_column(base_column + 1, PercentageFormat)
        self.table.format_column(base_column + 2, DollarFormat)
        self.table.format_column(base_column + 3, PercentageFormat)
        self.table.set_column_width(base_column + 2, 10) # revenue column needs some extra space

class ElasticityTable(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.label_frame = ttk.LabelFrame(self, text='Elasticity')
        self.label_frame.grid(row=0, column=0, sticky=tk.NSEW)
        self.table = Table(self.label_frame, ['Elasticity'], (0, 1), False)
        self.table.grid(row=0, column=0, sticky=tk.NSEW)

NUM_ITERS = 10
class ElasticityView(BoundFrame):
    def __do_simulation(self):
        print('simulate')
        iter_accounting = []
        for i in range(0, NUM_ITERS):
            summary = AccountingSummary()
            summary.account(self.tiers, self.data)
            iter_accounting.append(summary)
        self.elastic_summary.average(iter_accounting)
        self.elastic_summary_table.update_bindings()
        
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.baseline_summary = AccountingSummary()
        self.elastic_summary = AccountingSummary()
        self.tiers = None
        self.data = None
        
        self.tier_view = tier_widget.TierWidget(self)
        self.tier_view.grid(row=0, column=0, sticky=tk.NW)
        
        self.elasticity_table = ElasticityTable(self)
        self.elasticity_table.grid(row=0, column=1, sticky=tk.NW)
        
        self.elastic_summary_table = SummaryTable(self, self.elastic_summary, caption = 'Elastic')
        self.elastic_summary_table.grid(row=1, column=0, columnspan=3)
        self.baseline_summary_table = SummaryTable(self, self.baseline_summary, caption = 'Baseline', include_q_column = False)
        self.baseline_summary_table.grid(row=1, column=3)
        
        self.simulate_button = ttk.Button(self, text='Simulate', command=self.__do_simulation)
        self.simulate_button.grid(row=0, column=3)

    def set_tiers(self, ts):
        self.tiers = ts
        self.tier_view.set_tiers(ts)
        rows = len(ts.get_tiers())
        self.elasticity_table.table.set_dimensions(rows, 1)
        for r in range(0, rows):
            self.elasticity_table.table.set(r, 0, 1.0)
        if self.data:
            self.baseline_summary.account(self.tiers, self.data)
            self.baseline_summary_table.update_bindings()
            self.__do_simulation()

    def set_data(self, data):
        self.data = data
        if self.tiers:
            self.baseline_summary.account(self.tiers, self.data)
            self.baseline_summary_table.update_bindings()
            self.__do_simulation()
