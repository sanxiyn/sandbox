def ratio(numerator, denominator):
    if denominator == 0:
        return 0.0
    return float(numerator) / denominator

class Analytics(object):

    def __init__(self, periods, activity):
        self.periods = periods
        self.activity = activity

    def acquisition(self):
        self.cohorts = dict()
        for period in self.periods:
            self.cohorts[period] = list()
        for user in self.activity:
            first_active = self.activity[user][0]
            self.cohorts[first_active].append(user)

        self.all_count = len(self.activity)
        self.original_count = len(self.cohorts[self.periods[0]])
        self.acquisition_count = self.all_count - self.original_count
        self.acquisition_periods = self.periods[1:]
        self.acquisition_by_period = list()
        for period in self.acquisition_periods:
            count = len(self.cohorts[period])
            self.acquisition_by_period.append(count)

    def conversion(self):
        self.time_to_convert = dict()
        self.converted_cohorts = dict()
        for period in self.acquisition_periods:
            self.converted_cohorts[period] = list()
        for period in self.acquisition_periods:
            for user in self.cohorts[period]:
                active = self.activity[user]
                if len(active) == 1:
                    continue
                first_active = active[0]
                next_active = active[1]
                first_to_next = next_active - first_active
                self.time_to_convert[user] = first_to_next
                self.converted_cohorts[next_active].append(user)

        self.conversion_count = len(self.time_to_convert)
        self.conversion_ratio = ratio(
            self.conversion_count, self.acquisition_count)
        self.conversion_sum = 0
        for user in self.time_to_convert:
            self.conversion_sum += self.time_to_convert[user]
        self.average_time_to_convert = ratio(
            self.conversion_sum, self.conversion_count)
        conversion_cut = (
            self.acquisition_periods[-1] - int(self.average_time_to_convert))
        self.conversion_periods = list()
        self.conversion_cut_count = 0
        for period in self.acquisition_periods[1:]:
            if period < conversion_cut:
                self.conversion_periods.append(period)
            else:
                self.conversion_cut_count += 1
        self.conversion_by_period = list()
        for period in self.conversion_periods:
            count = len(self.converted_cohorts[period])
            self.conversion_by_period.append(count)

    def retention(self):
        self.retention_by_period = list()
        for i, period in enumerate(self.conversion_periods):
            users = self.converted_cohorts[period]
            retention = list()
            retention.append(len(users))
            later_periods = self.conversion_periods[i + 1:]
            for j, later_period in enumerate(later_periods):
                count = 0
                for user in users:
                    if later_period in self.activity[user]:
                        count += 1
                retention.append(count)
            self.retention_by_period.append(retention)
