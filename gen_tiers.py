import sys
from numpy import loadtxt, arange, ones
from scipy import stats

from rate_tier import RateTier, TierSystem
from RawQData import RawQData

data_file_dir = sys.argv[1]

tier_file_name = sys.argv[2]
spreadsheet_file_name = sys.argv[3]
raw = RawQData(data_file_dir)
lines = loadtxt(tier_file_name)
#print lines
rates = TierSystem()
for l in lines:
    rates.add_tier(RateTier(l[0], l[1], l[2]))

total_revenue = 0
total_volume = 0
for qd in raw.Qs:
    for v in qd:
        rates.account(v)
    total_revenue += rates.total_revenue()
    total_volume += rates.total_volume()
    #rates.dump();
    rates.clear_account()

print("total volume for the year: {0}".format(total_volume))
print("total revenue for the year: {0}".format(total_revenue))

print("applying elasticity:")
rates.set_elasticity([0.6, 0.6])
#rates.set_elasticity([0.6, 0.6, 0.6])

total_elastic_revenue = 0
total_elastic_volume = 0
for qd in raw.Qs:
    for v in qd:
        rates.account(v)
    total_elastic_revenue += rates.total_revenue()
    total_elastic_volume += rates.total_volume()
    #rates.dump();
    rates.clear_account()

print("total elastic volume for the year: {0} ({1}% reduction)".format(total_elastic_volume, 100.0 - (total_elastic_volume / total_volume * 100.0)))
print("total elastic revenue for the year: {0} ({1}% reduction)".format(total_elastic_revenue, 100.0 - (total_elastic_revenue / total_revenue * 100.0)))

rates.set_elasticity([1.0, 1.0, 1.0])
rates.account(110)
#rates.account(1489)
#rates.account(12600)
#rates.account(280)
rates.dump();

#rates.export(spreadsheet_file_name)
