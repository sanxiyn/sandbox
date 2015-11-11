import datetime
import os
import re

import matplotlib
matplotlib.use('cairo')

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def date_of_toolchain(toolchain):
    _, y, m, d = toolchain.split('-')
    return datetime.date(int(y), int(m), int(d))

def minmax_dates(dates):
    mind, maxd = min(dates), max(dates)
    dmin = datetime.date(mind.year, mind.month, 1)
    if maxd.month == 12:
        dmax = datetime.date(maxd.year + 1, 1, 1)
    else:
        dmax = datetime.date(maxd.year, maxd.month + 1, 1)
    return dmin, dmax

def get_path(toolchain, crate, profile):
    crate_root = os.path.join('toolchain', toolchain, crate)
    name, version = crate.split('-')
    filename = 'lib{}.rlib'.format(name)
    return os.path.join(crate_root, 'target', profile, filename)

def get_log_path(toolchain, crate):
    crate_root = os.path.join('toolchain', toolchain, crate)
    return os.path.join(crate_root, 'time.log')

time_pattern = re.compile(r'time: ([0-9.]+)')

def get_log_data(path):
    data = {}
    f = open(path)
    for line in f:
        line = line.strip()
        if not line.startswith('time: '):
            continue
        time_info, pass_name = line.split('\t')
        time = float(time_pattern.match(time_info).group(1))
        data.setdefault(pass_name, []).append(time)
    f.close()
    return data

def get_pass_data(toolchain, crate, pass_name):
    date = date_of_toolchain(toolchain)
    path = get_log_path(toolchain, crate)
    data = get_log_data(path)
    # See #27641
    if date >= datetime.date(2015, 8, 15):
        data['type checking'] = map(sum, zip(
            data['wf checking (old)'],
            data['item-types checking'],
            data['item-bodies checking'],
            data['drop-impl checking'],
            data['wf checking (new)']))
    return data[pass_name]

def avg_and_err(datas):
    avgs = [sum(data) / len(data) for data in datas]
    mins = [min(data) for data in datas]
    maxs = [max(data) for data in datas]
    merrs = [avg - mini for (avg, mini) in zip(avgs, mins)]
    perrs = [maxi - avg for (avg, maxi) in zip(avgs, maxs)]
    base = avgs[0]
    scaled_avgs = [avg / base * 100 for avg in avgs]
    scaled_merrs = [err / base * 100 for err in merrs]
    scaled_perrs = [err / base * 100 for err in perrs]
    return scaled_avgs, [scaled_merrs, scaled_perrs]

tools = sorted(os.listdir('toolchain'))
crates = sorted(os.listdir('crate'))

dates = [date_of_toolchain(tool) for tool in tools]
dmin, dmax = minmax_dates(dates)
x = [mdates.date2num(date) for date in dates]
xmin = mdates.date2num(dmin)
xmax = mdates.date2num(dmax)

def setup_x_axis(ax):
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.set_xlabel('Rust version')
    ax.set_xlim(xmin, xmax)
    for xi in x:
        ax.axvline(xi, color='black', linestyle='dotted')

def plot_size(ax, profile):
    for crate in crates:
        paths = [get_path(tool, crate, profile) for tool in tools]
        sizes = [float(os.path.getsize(path)) for path in paths]
        base = sizes[0]
        y = [size / base * 100 for size in sizes]
        ax.plot(x, y, label=crate)
    ax.set_title(profile.title())
    setup_x_axis(ax)
    ax.set_ylabel('size (%)')
    ax.set_ylim(60, 120)
    ax.axhline(100, color='black')
    ax.legend()

def figure_size():
    plt.figure(figsize=(12, 5))
    debug = plt.subplot(1, 2, 1)
    plot_size(debug, 'debug')
    release = plt.subplot(1, 2, 2)
    plot_size(release, 'release')
    plt.savefig('size.png')

def plot_time(ax, pass_name):
    for crate in crates:
        times = [get_pass_data(tool, crate, pass_name) for tool in tools]
        y, yerr = avg_and_err(times)
        ax.errorbar(x, y, yerr, label=crate)
    ax.set_title(pass_name.title())
    setup_x_axis(ax)
    ax.set_ylabel('time (%)')
    ax.axhline(100, color='black')
    ax.legend()

def figure_time():
    plt.figure(figsize=(12, 5))
    tc = plt.subplot(1, 2, 1)
    plot_time(tc, 'type checking')
    tr = plt.subplot(1, 2, 2)
    plot_time(tr, 'translation')
    plt.savefig('time.png')

figure_size()
figure_time()
