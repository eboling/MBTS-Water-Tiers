from numpy import loadtxt, arange, ones
from scipy import stats
from rate_tier import TierSystem, RateTier

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


class WaterAnalyzer:
    def __init__(self, q_data, logger):
        self.raw_Qs = q_data
        self.logger = logger
        self.raw_data = None
        self.median_value = 0
        self.tiers = []
        self.last_r_squared = -1
        self.first_tier_done = False
        self.second_tier_done = False
        self.start = 0

    def get_tier_system(self):
        ts = TierSystem()
        for t in self.tiers:
            ts.add_tier(t)
        return ts

    def calculate_largest_quarter(self):
        max_volume = 0
        max_quarter_number = 0
        q_num = 1
        for qd in self.raw_Qs.basic_stats():
            if qd[2] > max_volume:
                max_quarter_number = q_num
                max_volume = qd[2]
                self.raw_data = qd[3]
                self.median_value = qd[1]
                q_num += 1
        self.logger.log('selected quarter {0}, which had a total volume of {1} and a median of {2}'.format(max_quarter_number,
                                                                                                          max_volume, self.median_value))
    def get_tier(self, subrange):
        return (subrange[0], subrange[len(subrange) - 1])

    def should_break_tier(self, r_squared, subrange):
        if subrange[len(subrange) - 1] > (self.median_value * TIER_ONE_MEDIAN_FRACTION) and not self.first_tier_done:
            fractional_median_break = True
        else:
            fractional_median_break = False
        median_break = subrange[len(subrange) - 1] > self.median_value and not self.second_tier_done and self.first_tier_done
        if fractional_median_break or median_break:
            return True
        if r_squared < self.last_r_squared - R_SQUARED_EPSILON:
            tier = self.get_tier(subrange)
            if (tier[1] - tier[0] > TIER_VOLUME_BREAKING_THRESHOLD):
                #self.logger.log("breaking: {0}, {1}, {2}".format(r_squared, self.last_r_squared, tier[1] - tier[0]))
                return True
        return False
    
    def add_tier(self, low, high, count):
        t = RateTier(low, high, 0)
        t.count = count
        self.tiers.append(t)

    def collapse_tiers(self):
        new_t = []
        merge_t = None
        for t in self.tiers:
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
        self.tiers = new_t
        #return new_t

    def finalize_tiers(self):
        self.tiers[0].low_bound = 0.0
        for i in xrange(0, len(self.tiers) - 2):
            t = self.tiers[i]
            tn = self.tiers[i + 1]
            #tn.low_bound = t.high_bound + 1.0
            tn.low_bound = t.high_bound
            self.tiers[len(self.tiers) - 1].high_bound = 100000.0
        self.collapse_tiers()
        #tiers = self.collapse_tiers(tiers)
        #return self.tiers

    def set_prices(self):
        price = MINIMUM_TIER_PRICE
        price_delta = (LAST_TIER_PRICE - SECOND_TIER_PRICE) / (len(self.tiers) - 2)
        self.logger.log("price_delta = {0}".format(price_delta))
        first = True
        for t in self.tiers:
            t.rate = price
            #self.logger.log('{0} {1} {2}'.format(t.low_bound, t.high_bound, t.price))
            if first:
                first = False
                price = SECOND_TIER_PRICE
            else:
                price = price + price_delta
        for t in self.tiers:
            self.logger.log('{0} {1} {2}'.format(t.low_bound, t.high_bound, t.rate))

    def Analyze(self):
        self.logger.log('first pass analysis:')
        self.calculate_largest_quarter()
        while True:
            self.last_r_squared = -1
            broke_range = False
            for i in xrange(self.start, len(self.raw_data) - 4):
                subrange = self.raw_data[self.start:i + 4]
                xi = arange(0, len(subrange))
                slope, intercept, r_value, p_value, std_err = stats.linregress(xi,subrange)
                r_squared = r_value ** 2
                if self.should_break_tier(r_squared, subrange):
                    self.add_tier(subrange[0], subrange[len(subrange) - 1], len(subrange))
                    self.start = i + 1;
                    if self.first_tier_done:
                        self.second_tier_done = True
                    self.first_tier_done = True
                    broke_range = True
                    self.logger.log('tier: {0} - {1}, R^2 = {2}, len = {3}'.format(subrange[0], subrange[len(subrange) - 1], self.last_r_squared, len(subrange)))
                    break
                if r_squared > self.last_r_squared:
                    self.last_r_squared = r_squared
    
            # if we didn't break any range, across the full loop, we'll stop now, because
            # otherwise we'll iterate forever
            if not broke_range:
                self.add_tier(subrange[0], subrange[i - self.start - 1], len(subrange) - 1)
                self.logger.log('tier: {0} - {1}, R^2 = {2}, len = {3}'.format(subrange[0], subrange[len(subrange) - 2], self.last_r_squared, len(subrange) - 1))
                break
        
            if self.start > len(self.raw_data) - 8:
                break

        #self.tiers = self.finalize_tiers(self.tiers)
        self.finalize_tiers()
        self.set_prices()
        self.logger.log("Finalized tiers:");
        for t in self.tiers:
            t.log(self.logger)
        quantiles = stats.mstats.hdquantiles(self.raw_data, map(lambda x: x / 100.0, range(5, 100, 5)))
        quantiles = map(lambda x: int(round(x)), quantiles)
        self.logger.log('quantiles:')
        self.logger.log(str(quantiles))
