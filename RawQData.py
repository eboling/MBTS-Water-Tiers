import sys
import csv
from numpy import loadtxt, arange, ones
from scipy import stats

#
#  Accounting data may have multiple account entries in a single quarter, because of multiple services.
#  This routine collects those all down to a single account entry in the list, per account, with the
#  usage amount aggregated.  So [(act_A, 10), (act_A, 20)] -> [(act_a, 30)]
#
def collect_accounts(dict, usage_values):
    for t in usage_values:
        if t[0] in dict:
            v = dict[t[0]]
            dict[t[0]] = v + t[1]
        else:
            dict[t[0]] = t[1]

class BillableEntry:
    def __init__(self, id, usage):
        self.id = id
        self.usage = usage

def load_csv_water_usage(file_name, filter = lambda x: x):
    values = []
    with open(file_name, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        header = reader.next()
        #if (header[1] != 'acct_no') or (header[11] != 'act_usage'):
        if (header[0] != 'serv_id') or (header[12] != 'bill_usage'):
            raise Exception('water data in unknown column layout')
        for row in reader:
            try:
                if filter(row) is None:
                    continue
                #acct_number = int(row[1])
                acct_number = int(row[0])
                #values.append((acct_number, int(row[11])))
                values.append((acct_number, int(row[12])))
                if int(row[11]) / 100.0 > 2500.0:
                    print row
            except ValueError:
                continue
    d = {}
    collect_accounts(d, values)
    values = [(k, v) for k, v in d.iteritems()]
    #values = [BillableEntry(k, v) for k, v in d.iteritems()]
    return values

class RawQData:
    def __init__(self, directory, filter=lambda x: x):
        self.Qs = []
        #self.Qs.append(loadtxt(directory + "/Q1.txt"))
        #self.Qs.append(loadtxt(directory + "/Q2.txt"))
        #self.Qs.append(loadtxt(directory + "/Q3.txt"))
        #self.Qs.append(loadtxt(directory + "/Q4.txt"))
        self.Qs.append(load_csv_water_usage(directory + "/Q1.csv", filter))
        self.Qs.append(load_csv_water_usage(directory + "/Q2.csv", filter))
        self.Qs.append(load_csv_water_usage(directory + "/Q3.csv", filter))
        self.Qs.append(load_csv_water_usage(directory + "/Q4.csv", filter))
        for q in self.Qs:
            q.sort(key = lambda tup: tup[1])
        self.Qs = [ [ (x[0], x[1] / 100.0) for x in q] for q in self.Qs]
    def basic_stats(self):
        usage_numbers = [ [x[1] for x in q] for q in self.Qs]
        return [ (q[len(q) - 1], stats.mstats.hdmedian(q), sum(q), q) for q in usage_numbers]
    def collect_account_totals(self):
        d = {}
        for q in self.Qs:
            collect_accounts(d, q);
        return d.values()
    def summarize(self):
        i = 1
        for s in self.basic_stats():
            print("Q{0}: max = {1}, median = {2}, total = {3}".format(i, s[0], s[1], s[2]))
            i += 1

#raw = RawQData("2015")
#raw.summarize()
