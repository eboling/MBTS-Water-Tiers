import sys
import csv
from enum import Enum
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

class WaterService:
    def __init__(self, id):
        self.id = id
        self.on_well = False
        self.readings = []

    def get_on_well(self):
        return self.on_well
    
    def set_on_well(self, v):
        self.on_well = v

    def get_id(self):
        return self.id

class WaterServices:
    def __init__(self):
        self.services = {}

    def get_service(self, id):
        if not id in self.services:
            self.services[id] = WaterService(id)
        return self.services[id]

    def get_services(self):
        return self.services.values()

class WaterVolumeUnits(Enum):
    HCF = 1
    GALLONS = 2

    @classmethod
    def convert(cls, from_units, to_units, value):
        if from_units != to_units:
            if from_units == cls.HCF:
                # HCF -> gallons
                value = value * 100.0 * 7.48052
            else:
                # gallons -> HCF
                value = (value * 0.13368) / 100.0
        return value
        

class MeterReading:
    def __init__(self, service, usage):
        self.service = service
        self.usage = usage
        self.units = WaterVolumeUnits.HCF
        self.reporting_units = WaterVolumeUnits.HCF
        service.readings.append(self)

    def get_billable_usage(self):
        if self.service.get_on_well():
            return 0
        return WaterVolumeUnits.convert(self.units, self.reporting_units, self.usage)
    
    def get_usage(self):
        return WaterVolumeUnits.convert(self.units, self.reporting_units, self.usage)
    
    def set_usage(self, v):
        self.usage = v

    def get_service(self):
        return self.service

class RawQData:
    def __init__(self, directory, filter=lambda x: x):
        self.services = WaterServices()
        self.Qs = []
        #self.Qs.append(loadtxt(directory + "/Q1.txt"))
        #self.Qs.append(loadtxt(directory + "/Q2.txt"))
        #self.Qs.append(loadtxt(directory + "/Q3.txt"))
        #self.Qs.append(loadtxt(directory + "/Q4.txt"))
        self.Qs.append(self.load_csv_water_usage(directory + "/Q1.csv", filter))
        self.Qs.append(self.load_csv_water_usage(directory + "/Q2.csv", filter))
        self.Qs.append(self.load_csv_water_usage(directory + "/Q3.csv", filter))
        self.Qs.append(self.load_csv_water_usage(directory + "/Q4.csv", filter))
        for q in self.Qs:
            q.sort(key = lambda tup: tup.get_usage())
            #q.sort(key = lambda tup: tup[1])
        #self.Qs = [ [ (x[0], x[1] / 100.0) for x in q] for q in self.Qs]

    """Sets the WaterVolumeUnits type that readings in this batch of data will report."""
    def set_reporting_units(self, units):
        for q in self.Qs:
            for mr in q:
                mr.reporting_units = units

    '''Returns the index of the quarter with the heaviest usage.'''
    def heaviest_quarter(self):
        # gen returns a generator that is the list of usage numbers for a quarter
        gen = lambda q: (x.get_usage() for x in q)
        # summation returns the sum of usages in a quarter
        summation = lambda q: sum(gen(q))
        usage_totals = [summation(q) for q in self.Qs]
        return usage_totals.index(max(usage_totals))
        
    '''Returns the index of the quarter with the lightest usage.'''
    def lightest_quarter(self):
        # gen returns a generator that is the list of usage numbers for a quarter
        gen = lambda q: (x.get_usage() for x in q)
        # summation returns the sum of usages in a quarter
        summation = lambda q: sum(gen(q))
        usage_totals = [summation(q) for q in self.Qs]
        return usage_totals.index(min(usage_totals))
        
    def load_csv_water_usage(self, file_name, filter):
        d = {}
        with open(file_name, 'r') as csvfile:
            reader = csv.reader(csvfile)
#            header = reader.next()
            header = next(reader)
            if (header[0] != 'serv_id') or (header[12] != 'bill_usage'):
                raise Exception('water data in unknown column layout')
            for row in reader:
                try:
                    if filter(row) is None:
                        continue
                    #acct_number = int(row[1])
                    acct_number = int(row[0])
                    service = self.services.get_service(acct_number)
                    usage = int(row[12]) / 100.0
                    if service in d:
                        reading = d[service]
                        reading.set_usage(reading.get_usage() + usage)
                    else:
                        reading = MeterReading(service, usage)
                        d[service] = reading
                    if usage > 2500.0:
                        print(row)
                except ValueError:
                    continue
        return [v for k, v in d.items()]

    def basic_stats(self):
        #usage_numbers = [ [x[1] for x in q] for q in self.Qs]
        usage_numbers = [ [x.get_usage() for x in q] for q in self.Qs]
        return [ (q[len(q) - 1], stats.mstats.hdmedian(q), sum(q), q) for q in usage_numbers]
    def collect_account_totals(self):
        d = {}
        for q in self.Qs:
            for reading in q:
                if reading.get_service() in d:
                    v = d[reading.get_service()]
                    v.set_usage(v.get_usage() + reading.get_usage())
                else:
                    d[reading.get_service()] = MeterReading(reading.get_service(), reading.get_usage())
        return [v for k, v in d.items()]
    def summarize(self):
        i = 1
        for s in self.basic_stats():
            print("Q{0}: max = {1}, median = {2}, total = {3}".format(i, s[0], s[1], s[2]))
            i += 1
