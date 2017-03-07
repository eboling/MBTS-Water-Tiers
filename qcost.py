import sys
from numpy import loadtxt, arange, ones
from scipy import stats

from rate_tier import RateTier, TierSystem
from RawQData import RawQData

#data_file_dir = sys.argv[1]

tier_file_name = sys.argv[1]
lines = loadtxt(tier_file_name)
rates = TierSystem()
for l in lines:
    rates.add_tier(RateTier(l[0], l[1], l[2]))

rates.account(int(sys.argv[2]))
rates.dump()
