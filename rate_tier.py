import sys

class RateTier:
    def __init__(self, low, high, rate):
        self.low_bound = low
        self.high_bound = high
        self.rate = rate
        self.count = 0
        self.total_volume = 0
        self.tier_volume = 0
        self.revenue = 0
    def dump(self):
        print('{0} - {1} rate = {2}, count = {3}, total_volume = {4}, tier_volume = {5}, revenue = {6}'.format(self.low_bound, self.high_bound, self.rate, self.count, self.total_volume, self.tier_volume, self.revenue))
    def account(self, volume):
        return

class TierSystem:
    def __init__(self):
        self.tiers = []
    def add_tier(self, tier):
        self.tiers.append(tier)
    def account(self, volume):
        for tier in self.tiers:
            v = min(volume, tier.high_bound) - tier.low_bound - 1
            tier.revenue += v * tier.rate
            tier.total_volume += v
            if volume <= tier.high_bound:
                tier.tier_volume += volume
                tier.count += 1
                break
    def clear_account(self):
        for t in self.tiers:
            t.revenue = 0
            t.total_volume = 0
            t.tier_volume = 0
            t.count = 0
    def total_revenue(self):
        total = 0.0;
        for t in self.tiers:
            total += t.revenue;
        return total
    def dump(self):
        total = 0;
        for tier in self.tiers:
            tier.dump()
            total += tier.revenue;
        print('total revenue = {0}'.format(total))
    def export(self, filename):
        f = open(filename, 'w')
        idx = 2
        f.write('"Range","Count","Volume","Rate","Revenue"\n')
        for t in self.tiers:
            f.write('"{0} - {1}",{2},{3},{4},=(C{5}*D{5})\n'.format(t.low_bound, t.high_bound, t.count, t.total_volume, t.rate, idx))
            idx += 1
        f.write('"","","","",=SUM(E2:E{0})\n'.format(len(self.tiers) + 1))
        f.close()
