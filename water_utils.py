from RawQData import RawQData
from rate_tier import RateTier, TierSystem

'''Returns a list of users in the uppermost quantile in the heaviest usage quarter.  Quantile is specified by the caller'''
def get_quantile_users(q_data, quantile):
    q = q_data.Qs[q_data.heaviest_quarter()]
    q = list(q)
    q.sort(key = lambda x: x.get_usage(), reverse = True)
    count = int(quantile * len(q))
    return q[:count]

'''Takes a RawQData, and a TierSystem, and does accounting for all quarters in the data.
Clears the accounting information in the tier system before doing the accounting.'''
def do_accounting(q_data, tiers):
    tiers.clear_account()
    for q in q_data.Qs:
        for v in q:
            tiers.account(v.get_billable_usage())

'''Returns the difference and percentage difference of two numbers.'''
def diff_pct(v, baseline):
    diff = v - baseline
    pct = (diff / baseline) * 100.0
    return diff, pct
