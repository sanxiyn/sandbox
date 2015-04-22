# pip install GitPython

from git import Repo

from analytics import Analytics

def parse_month(month_string):
    year, month = month_string.split('-')
    return (int(year), int(month))

def add_month(first_month, month_count):
    year, month = first_month
    y, m = divmod(month_count, 12)
    return (year + y, month + m)

def format_month((year, month)):
    month_format = '{:04}-{:02}'
    return month_format.format(year, month)

def commits_in_month(repo, (year, month)):
    date_format = '{:04}-{:02}-{:02}'
    after = date_format.format(year, month, 1)
    if month == 12:
        before = date_format.format(year + 1, 1, 1)
    else:
        before = date_format.format(year, month + 1, 1)
    return repo.iter_commits(after=after, before=before, no_merges=True)

def repo_activity(repo, first_month, month_count):
    activity = dict()
    for period in range(month_count):
        month = add_month(first_month, period)
        print '\rProcessing {}'.format(format_month(month)),
        for commit in commits_in_month(repo, month):
            user = commit.author.email
            if user not in activity:
                activity[user] = set()
            activity[user].add(period)
    for user in activity:
        activity[user] = sorted(activity[user])
    print '\nDone\n'
    return activity

import sys
args = sys.argv[1:]
if len(args) != 3:
    print 'Usage: cohort.py path/to/repo yyyy-mm month_count'
    sys.exit()
repo_path, first_month_string, month_count_string = args

repo = Repo(repo_path)
first_month = parse_month(first_month_string)
month_count = int(month_count_string)

periods = range(month_count)
activity = repo_activity(repo, first_month, month_count)
analytics = Analytics(periods, activity)

def format_counts(counts):
    return ','.join(str(count) for count in counts)

def format_counts_list(counts_list):
    return '\n'.join(format_counts(counts) for counts in counts_list)

analytics.acquisition()
print '''\
Acquisition analysis
{} contributors
{} contributors in original cohort
{} new contributors
New contributors in {} months
(excluding first month)
{}
'''.format(
    analytics.all_count,
    analytics.original_count,
    analytics.acquisition_count,
    len(analytics.acquisition_periods),
    format_counts(analytics.acquisition_by_period))

analytics.conversion()
print '''\
Conversion analysis
{} new repeat contributors
{}% conversion ({}/{})
{:.1f} months to convert in average ({}/{})
New repeat contributors in {} months
(excluding first 2 months and last {} months)
{}
'''.format(
    analytics.conversion_count,
    int(round(analytics.conversion_ratio * 100)),
    analytics.conversion_count, analytics.acquisition_count,
    analytics.average_time_to_convert,
    analytics.conversion_sum, analytics.conversion_count,
    len(analytics.conversion_periods),
    analytics.conversion_cut_count,
    format_counts(analytics.conversion_by_period))

analytics.retention()
print '''\
Retention analysis
{}
'''.format(
    format_counts_list(analytics.retention_by_period))
