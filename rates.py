import sys
from numpy import loadtxt, arange, ones
from scipy import stats
from rate_tier import RateTier

R_SQUARED_EPSILON = 0.02
TIER_VOLUME_BREAKING_THRESHOLD = 40
TIER_MINIMUM_COUNT = 40

raw_data_file_name = sys.argv[1]

tier_file_name = sys.argv[2]
tier_file = open(tier_file_name, 'w')

raw_data = loadtxt(raw_data_file_name)
raw_data.sort()
raw_data = [ x / 100.0 for x in raw_data ]

start = 0
first_tier_done = False
median_value = stats.mstats.hdmedian(raw_data)

tiers = []

def get_tier(subrange):
    return (subrange[0], subrange[len(subrange) - 1])

last_r_squared = -1
def should_break_tier(r_squared, subrange):
    median_break = subrange[len(subrange) - 1] > median_value and not first_tier_done
    if median_break:
        return True
    if r_squared < last_r_squared - R_SQUARED_EPSILON:
        tier = get_tier(subrange)
        #if (tier[1] - tier[0] > 150):
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
    print tiers
    return tiers

#    t = tiers[len(tiers) - 1]
#    tiers[len(tiers) - 1] = (t[0], raw_data[len(raw_data) - 1], 0)
#    for i in range(1, len(tiers) - 2): 
#       t = tiers[i]
#        tiers[i] = (t[0] + 1, t[1], 0)

print('hello there')
print('median = {0}'.format(median_value))
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
for t in tiers:
    t.dump()

#q = stats.mstats.hdquantiles(raw_data, [0.25, 0.50, 0.75])
#q = stats.mstats.hdquantiles(raw_data, [0.125, 0.25, 0.375, 0.50, 0.625, 0.75, 0.875])
q = stats.mstats.hdquantiles(raw_data, [0.50, 0.625, 0.75, 0.875])
print("quantiles:")
print q
last_low = 0
#for t in q:
#    tier_file.write('{0}.0 {1}.0 0\n'.format(last_low, round(t)))
#    last_low = round(t) + 1

for t in tiers:
    tier_file.write('{0} {1} 0\n'.format(t.low_bound, t.high_bound))

tier_file.close()

