import datetime
import os

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

tools = sorted(os.listdir('toolchain'))
crates = sorted(os.listdir('crate'))

dates = [date_of_toolchain(tool) for tool in tools]
dmin, dmax = minmax_dates(dates)
x = [mdates.date2num(date) for date in dates]
xmin = mdates.date2num(dmin)
xmax = mdates.date2num(dmax)

def plot_size(ax, profile):
    for crate in crates:
        paths = [get_path(tool, crate, profile) for tool in tools]
        sizes = [float(os.path.getsize(path)) for path in paths]
        base = sizes[0]
        y = [size / base * 100 for size in sizes]
        ax.plot(x, y, label=crate)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.set_title(profile.title())
    ax.set_xlabel('Rust version')
    ax.set_xlim(xmin, xmax)
    for xi in x:
        ax.axvline(xi, color='black', linestyle='dotted')
    ax.set_ylabel('size (%)')
    ax.set_ylim(60, 120)
    ax.axhline(100, color='black')
    ax.legend()

plt.figure(figsize=(12, 5))
debug = plt.subplot(1, 2, 1)
plot_size(debug, 'debug')
release = plt.subplot(1, 2, 2)
plot_size(release, 'release')
plt.savefig('size.png')
