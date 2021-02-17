#from rate_tier import TierSystem, RateTier

class QuarterlySummary:
    def __init__(self, volume = 0, revenue = 0.0):
        self.volume = volume
        self.revenue = revenue

    def clear(self):
        self.volume = 0
        self.revenue = 0.0
        
class AccountingSummary:
    def __init__(self):
        self.quarterly_information = [QuarterlySummary(), QuarterlySummary(), QuarterlySummary(), QuarterlySummary()]
        self.clear()

    def clear(self):
        self.annual_volume = 0
        self.annual_revenue = 0
        for qi in self.quarterly_information:
            qi.clear()

    def add(self, accounting_summary):
        self.annual_volume += accounting_summary.annual_volume
        self.annual_revenue += accounting_summary.annual_revenue
        for qs, oqs in zip(self.quarterly_information, accounting_summary.quarterly_information):
            qs.volume += oqs.volume
            qs.revenue += oqs.revenue
        count += 1

    def average(self, as_list):
        self.clear()
        for x in as_list:
            self.annual_volume += x.annual_volume
            self.annual_revenue += x.annual_revenue
            for qs, oqs in zip(self.quarterly_information, x.quarterly_information):
                qs.volume += oqs.volume
                qs.revenue += oqs.revenue
        n = len(as_list)
        self.annual_volume /= n
        self.annual_revenue /= n
        for qs in self.quarterly_information:
            print(qs.volume)
            qs.volume /= n
            qs.revenue /= n

    def percentages(self, q_num):
        volume_pct = self.quarterly_information[q_num].volume / self.annual_volume * 100.0
        revenue_pct = self.quarterly_information[q_num].revenue / self.annual_revenue * 100.0
        return volume_pct, revenue_pct

    def account(self, ts, Qs):
        self.clear()
        ts.clear_account()
        for q in Qs.Qs:
            for v in q:
                ts.account(v.get_billable_usage())
        self.annual_volume = ts.total_volume()
        self.annual_revenue = ts.total_revenue()
        ts.clear_account()
        for q, qi in zip(Qs.Qs, self.quarterly_information):
            ts.clear_account()
            for v in q:
                ts.account(v.get_billable_usage())
            qi.volume = ts.total_volume()
            qi.revenue = ts.total_revenue()
