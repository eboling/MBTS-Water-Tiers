import sys
from numpy import loadtxt, arange, ones
from scipy import stats

from rate_tier import RateTier, TierSystem

Q1_data_file_name = sys.argv[1]
Q2_data_file_name = sys.argv[2]
Q3_data_file_name = sys.argv[3]
Q4_data_file_name = sys.argv[4]

tier_file_name = sys.argv[5]
spreadsheet_file_name = sys.argv[6]
lines = loadtxt(tier_file_name)
#print lines
rates = TierSystem()
for l in lines:
    rates.add_tier(RateTier(l[0], l[1], l[2]))


def load_raw_data(fname):
    raw = loadtxt(fname)
    raw.sort()
    raw = [ x / 100.0 for x in raw ]
    return raw

#Q1_data = load_raw_data(Q1_data_file_name)
#Q2_data = load_raw_data(Q2_data_file_name)
#Q3_data = load_raw_data(Q3_data_file_name)
#Q4_data = load_raw_data(Q4_data_file_name)
Q_data = [ load_raw_data(Q1_data_file_name),
           load_raw_data(Q2_data_file_name),
            load_raw_data(Q3_data_file_name),
            load_raw_data(Q4_data_file_name)]
    
total_revenue = 0
for Q in Q_data:
    for v in Q:
        rates.account(v)
    total_revenue += rates.total_revenue()
    rates.dump();
    rates.clear_account()

print("total for the year: {0}".format(total_revenue))
#rates.account(12600)

#rates.dump();
#rates.export(spreadsheet_file_name)
