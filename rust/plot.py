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
mem_pattern = re.compile(r'rss: ([0-9]+)MB')

def get_log_data(path, pattern):
    data = {}
    f = open(path)
    for line in f:
        line = line.strip()
        if not line.startswith('time: '):
            continue
        pass_info, pass_name = line.split('\t')
        value = float(pattern.search(pass_info).group(1))
        data.setdefault(pass_name, []).append(value)
    f.close()
    return data

def get_pass_data(toolchain, crate, pass_name, pattern):
    date = date_of_toolchain(toolchain)
    path = get_log_path(toolchain, crate)
    data = get_log_data(path, pattern)
    # See #30389
    if date < datetime.date(2015, 12, 19):
        data['wf checking'] = map(sum, zip(
            data['wf checking (old)'],
            data['wf checking (new)']))
    # See #27641
    if date >= datetime.date(2015, 8, 15):
        passes = [
            'wf checking',
            'item-types checking',
            'item-bodies checking'
        ]
        # See #40178
        if date < datetime.date(2017, 3, 3):
            passes.append('drop-impl checking')
        data['type checking'] = map(sum, zip(
            *(data[pass_] for pass_ in passes)))
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
    lines = []
    for crate in crates:
        paths = [get_path(tool, crate, profile) for tool in tools]
        sizes = [float(os.path.getsize(path)) for path in paths]
        base = sizes[0]
        y = [size / base * 100 for size in sizes]
        line, = ax.plot(x, y, label=crate)
        lines.append(line)
    ax.set_title(profile.title())
    setup_x_axis(ax)
    ax.set_ylabel('size (%)')
    ax.set_ylim(60, 120)
    ax.axhline(100, color='black')
    return lines

def figure_size():
    fig = plt.figure(figsize=(12, 6))
    debug = plt.subplot(1, 2, 1)
    lines = plot_size(debug, 'debug')
    release = plt.subplot(1, 2, 2)
    plot_size(release, 'release')
    plt.subplots_adjust(bottom=0.2)
    fig.legend(lines, crates, 'lower center', ncol=5)
    plt.savefig('size-2.png')

def plot_time(ax, pass_name, display_name=None):
    if display_name is None:
        display_name = pass_name
    lines = []
    for crate in crates:
        times = [get_pass_data(tool, crate, pass_name, time_pattern)
            for tool in tools]
        y, yerr = avg_and_err(times)
        line, _, _ = ax.errorbar(x, y, yerr, label=crate)
        lines.append(line)
    ax.set_title(display_name.title())
    setup_x_axis(ax)
    ax.set_ylabel('time (%)')
    ax.set_ylim(50, 150)
    ax.axhline(100, color='black')
    return lines

def figure_time():
    fig = plt.figure(figsize=(12, 6))
    tc = plt.subplot(1, 2, 1)
    lines = plot_time(tc, 'item-bodies checking', 'type checking')
    tr = plt.subplot(1, 2, 2)
    plot_time(tr, 'translation')
    plt.subplots_adjust(bottom=0.2)
    fig.legend(lines, crates, 'lower center', ncol=5)
    plt.savefig('time-5.png')

def plot_mem(ax, pass_name, display_name=None):
    if display_name is None:
        display_name = pass_name
    lines = []
    for crate in crates:
        mems = [get_pass_data(tool, crate, pass_name, mem_pattern)
            for tool in tools]
        y, yerr = avg_and_err(mems)
        line, _, _ = ax.errorbar(x, y, yerr, label=crate)
        lines.append(line)
    ax.set_title(display_name.title())
    setup_x_axis(ax)
    ax.set_ylabel('mem (%)')
    ax.set_ylim(50, 150)
    ax.axhline(100, color='black')
    return lines

def figure_mem():
    fig = plt.figure(figsize=(8, 5))
    ax = plt.subplot(1, 1, 1)
    lines = plot_mem(ax, 'translation', 'memory')
    plt.subplots_adjust(right=0.625)
    fig.legend(lines, crates)
    plt.savefig('mem-5.png')

figure_time()
figure_mem()
