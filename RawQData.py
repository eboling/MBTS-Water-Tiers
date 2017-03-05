import sys
import csv
from numpy import loadtxt, arange, ones
from scipy import stats

def load_csv_water_usage(file_name):
    values = []
    with open(file_name, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        header = reader.next()
        if (header[1] != 'acct_no') or (header[11] != 'act_usage'):
            raise Exception('water data in unknnown column layout')
        for row in reader:
            try:
                acct_number = int(row[1])
                values.append((acct_number, int(row[11])))
            except ValueError:
                continue
    return values

class RawQData:
    def __init__(self, directory):
        self.Qs = []
        #self.Qs.append(loadtxt(directory + "/Q1.txt"))
        #self.Qs.append(loadtxt(directory + "/Q2.txt"))
        #self.Qs.append(loadtxt(directory + "/Q3.txt"))
        #self.Qs.append(loadtxt(directory + "/Q4.txt"))
        self.Qs.append(load_csv_water_usage(directory + "/Q1.csv"))
        self.Qs.append(load_csv_water_usage(directory + "/Q2.csv"))
        self.Qs.append(load_csv_water_usage(directory + "/Q3.csv"))
        self.Qs.append(load_csv_water_usage(directory + "/Q4.csv"))
        for q in self.Qs:
            q.sort(key = lambda tup: tup[1])
        self.Qs = [ [ (x[0], x[1] / 100.0) for x in q] for q in self.Qs]
    def basic_stats(self):
        usage_numbers = [ [x[1] for x in q] for q in self.Qs]
        return [ (q[len(q) - 1], stats.mstats.hdmedian(q), sum(q), q) for q in usage_numbers]
    def collect_account_totals(self):
        d = {}
        for q in self.Qs:
            for t in q:
                if t[0] in d:
                    v = d[t[0]]
                    d[t[0]] = v + t[1]
                else:
                    d[t[0]] = t[1]
        return d.values()
    def summarize(self):
        i = 1
        for s in self.basic_stats():
            print("Q{0}: max = {1}, median = {2}, total = {3}".format(i, s[0], s[1], s[2]))
            i += 1

#raw = RawQData("2015")
#raw.summarize()
