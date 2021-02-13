import sys
import RawQData
import rate_tier
from scipy import stats

raw_Qs = RawQData.RawQData(sys.argv[1])
heavy_q = raw_Qs.Qs[raw_Qs.heaviest_quarter()]
usage = [v.get_billable_usage() for v in heavy_q]

total=sum(usage)
total_users=len(usage)
print("total usage in heavy q: {0}".format(total))
print("total users: {0}".format(total_users))
pct = 0.05
cum = 0
num_users = 0
cum_users = 0
usage.sort()
for x in usage:
    cum += x
    if ((cum / total) >= pct):
        print("{0}: {1} ({2}%/{3}%)".format(int(round(pct * 100.0)),
                                                num_users,
                                                int(round((float(num_users) / float(total_users)) * 100.0)),
                                                int(round((float(cum_users) / float(total_users)) * 100.0))))
        num_users = 0
        pct += 0.05
    else:
        num_users += 1
        cum_users += 1

quantiles = stats.mstats.hdquantiles(usage, [x / 100.0 for x in range(5, 100, 5)])
quantiles = [int(round(x)) for x in quantiles]

print('quantiles:')
print(quantiles)

def q_median_info(raw_qs, q_num):
    print(f"Q{q_num+1}:")
    q = raw_Qs.Qs[q_num]
    usage = [v.get_billable_usage() for v in q]
    total=sum(usage)
    total_users=len(usage)
    cum = 0
    n = 0
    for u in usage:
        cum += u
        n += 1
        if n > total_users/2:
            break
    print(f"  Total usage at median point: {cum} ({(cum/sum(usage)) * 100.0}%)")
    
q_median_info(raw_Qs, 0)
q_median_info(raw_Qs, 1)
q_median_info(raw_Qs, 2)
q_median_info(raw_Qs, 3)
