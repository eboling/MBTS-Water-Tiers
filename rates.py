import sys
from numpy import loadtxt, arange, ones
from scipy import stats
from rate_tier import RateTier
from RawQData import RawQData

#
#  This program reads in 4 quarters of water usage data, and generates suggested tier breakouts, based on
#  some heuristics.
#

MINIMUM_TIER_PRICE = 5.43
SECOND_TIER_PRICE = 6.0
LAST_TIER_PRICE = 10.0

'''R^2 deviation from the best fit achieved at which we decide a tier needs to be broken out.'''
R_SQUARED_EPSILON = 0.02

'''Volume, in HCF, that is the minimum to establish a tier'''
TIER_VOLUME_BREAKING_THRESHOLD = 40

'''Minimum count of users in a tier.'''
TIER_MINIMUM_COUNT = 40

'''Fraction of median value at which we break out the first tier.'''
TIER_ONE_MEDIAN_FRACTION=0.5

raw_data_dir = sys.argv[1]

tier_file_name = sys.argv[2]
tier_file = open(tier_file_name, 'w')

raw_Qs = RawQData(raw_data_dir)

account_totals = raw_Qs.collect_account_totals()
print "total accounts = {0}, total volume = {1}".format(len(account_totals), sum(account_totals))

# find the maximum volume quarter.  The data structures suck for this - rethink them
max_volume = 0
max_quarter_number = 0
q_num = 1
for qd in raw_Qs.basic_stats():
    if qd[2] > max_volume:
        max_quarter_number = q_num
        max_volume = qd[2]
        raw_data = qd[3]
        median_value = qd[1]
    q_num += 1
print ('selected quarter {0}, which had a total volume of {1} and a median of {2}'.format(max_quarter_number, max_volume, median_value))

start = 0
first_tier_done = False
second_tier_done = False
#median_value = stats.mstats.hdmedian(raw_data)

tiers = []

def get_tier(subrange):
    return (subrange[0], subrange[len(subrange) - 1])

last_r_squared = -1
def should_break_tier(r_squared, subrange):
    fractional_median_break = subrange[len(subrange) - 1] > (median_value * TIER_ONE_MEDIAN_FRACTION) and not first_tier_done
    median_break = subrange[len(subrange) - 1] > median_value and not second_tier_done and first_tier_done
    if fractional_median_break or median_break:
        return True
    if r_squared < last_r_squared - R_SQUARED_EPSILON:
        tier = get_tier(subrange)
        if (tier[1] - tier[0] > TIER_VOLUME_BREAKING_THRESHOLD):
            return True
    return False

def add_tier(ts, low, high, count):
    t = RateTier(low, high, 0)
    t.count = count
    ts.append(t)
    #ts.append((low, high, 0, count));

def collapse_tiers(tiers):
    new_t = []
    merge_t = None
    for t in tiers:
        if t.count < TIER_MINIMUM_COUNT:
            if merge_t is None:
                merge_t = t
            else:
                merge_t.count += t.count
                merge_t.high_bound = t.high_bound
            if merge_t.count >= TIER_MINIMUM_COUNT:
                new_t.append(merge_t)
                merge_t = None
        else:
            if not merge_t is None:
                new_t.append(merge_t)
                merge_t = None
            new_t.append(t)
    if not merge_t is None:
        new_t.append(merge_t)
    return new_t

def finalize_tiers_old():
    last_high = 0
    tiers[0] = (0, tiers[0][1], 0, tiers[0][3])
    for i in range(0, len(tiers) - 2):
        t = tiers[i]
        tn = tiers[i + 1]
        tn = (t[1] + 1, tn[1], 0, tn[3])
        tiers[i + 1] = tn
    collapse_tiers()
    print tiers

def finalize_tiers(tiers):
    tiers[0].low_bound = 0.0
    for i in range(0, len(tiers) - 2):
        t = tiers[i]
        tn = tiers[i + 1]
        tn.low_bound = t.high_bound + 1.0
    tiers[len(tiers) - 1].high_bound = 100000.0
    tiers = collapse_tiers(tiers)
    #print tiers
    return tiers

#    t = tiers[len(tiers) - 1]
#    tiers[len(tiers) - 1] = (t[0], raw_data[len(raw_data) - 1], 0)
#    for i in range(1, len(tiers) - 2): 
#       t = tiers[i]
#        tiers[i] = (t[0] + 1, t[1], 0)

#print('hello there')
#print('median = {0}'.format(median_value))
print('first pass analysis:')
while True:
    last_r_squared = -1
    broke_range = False
    for i in range(start, len(raw_data) - 4):
        subrange = raw_data[start:i + 4]
        xi = arange(0, len(subrange))
        slope, intercept, r_value, p_value, std_err = stats.linregress(xi,subrange)
        r_squared = r_value ** 2
        if should_break_tier(r_squared, subrange):
            #            add_tier(subrange[0], subrange[len(subrange) - 1])
            #add_tier(tiers, subrange[0], subrange[i - start - 1], len(subrange) - 1)
            add_tier(tiers, subrange[0], subrange[len(subrange) - 1], len(subrange))
            start = i + 1;
            if first_tier_done:
                second_tier_done = True
            first_tier_done = True
            broke_range = True
            #print('tier: {0} - {1}, R^2 = {2}, len = {3}'.format(subrange[0], subrange[len(subrange) - 2], last_r_squared, len(subrange) - 1))
            print('tier: {0} - {1}, R^2 = {2}, len = {3}'.format(subrange[0], subrange[len(subrange) - 1], last_r_squared, len(subrange)))
            break
        if r_squared > last_r_squared:
            last_r_squared = r_squared
    
    # if we didn't break any range, across the full loop, we'll stop now, because
    # otherwise we'll iterate forever
    if not broke_range:
        add_tier(tiers, subrange[0], subrange[i - start - 1], len(subrange) - 1)
        print('tier: {0} - {1}, R^2 = {2}, len = {3}'.format(subrange[0], subrange[len(subrange) - 2], last_r_squared, len(subrange) - 1))
        break
        
    if start > len(raw_data) - 8:
        break

tiers = finalize_tiers(tiers)
print('finalized tiers:')
for t in tiers:
    t.dump()

#q = stats.mstats.hdquantiles(raw_data, [0.25, 0.50, 0.75])
#q = stats.mstats.hdquantiles(raw_data, [0.125, 0.25, 0.375, 0.50, 0.625, 0.75, 0.875])
q = stats.mstats.hdquantiles(raw_data, [0.50, 0.625, 0.75, 0.875, 0.995])
print("quantiles [0.50, 0.625, 0.75, 0.875, 0.995]:")
print q
last_low = 0
#for t in q:
#    tier_file.write('{0}.0 {1}.0 0\n'.format(last_low, round(t)))
#    last_low = round(t) + 1

price = MINIMUM_TIER_PRICE
price_delta = (LAST_TIER_PRICE - SECOND_TIER_PRICE) / (len(tiers) - 2)
print "price_delta = {0}".format(price_delta)
first = True
for t in tiers:
    tier_file.write('{0} {1} {2}\n'.format(t.low_bound, t.high_bound, price))
    if first:
        first = False
        price = SECOND_TIER_PRICE
    else:
        price = price + price_delta

tier_file.close()

