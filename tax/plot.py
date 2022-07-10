# 소비자물가상승률 (통계청, 2021)
# https://www.index.go.kr/potal/stts/idxMain/selectPoSttsIdxSearch.do?idx_cd=4226&stts_cd=422601

price_levels_start = 1965
price_levels = [
    2.6, 2.9, 3.2, 3.6, 4.0,
    4.7, 5.3, 5.9, 6.1, 7.6, 9.5, 10.9, 12.0, 13.8, 16.3,
    21.0, 25.4, 27.3, 28.2, 28.8, 29.6, 30.4, 31.3, 33.5, 35.4,
    38.5, 42.1, 44.7, 46.8, 49.8, 52.0, 54.6, 57.0, 61.3, 61.8,
    63.2, 65.7, 67.5, 69.9, 72.4, 74.4, 76.1, 78.0, 81.7, 83.9,
    86.4, 89.9, 91.8, 93.0, 94.2, 94.9, 95.8, 97.6, 99.1, 99.5,
    100.0, 102.5
]

def get_price_level(year):
    return price_levels[year - price_levels_start]

# 한국 조세제도의 발전과정과 현황 (국회예산정책처, 2018)
# https://viewer.nabo.go.kr/streamdocs/view/sd;streamdocsId=72059251478892343
# [표 21] 1975~2018년 소득세율과 과표구간 변화 (pp. 128-129)

brackets = {} # 단위 만원
rates = {}    # 단위 %

brackets[1975] = [24, 48, 72, 96, 120, 150, 180, 240, 300, 480, 720, 1200, 2400, 3600, 4800]
rates[1975] = [8, 10, 12, 15, 18, 21, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70]
brackets[1989] = [250, 500, 800, 1200, 1700, 2300, 5000]
rates[1989] = [5, 10, 15, 20, 25, 30, 40, 50]
brackets[1991] = [400, 1000, 2500, 5000]
rates[1991] = [5, 16, 27, 38, 50]
brackets[1994] = [400, 800, 1600, 3200, 6400]
rates[1994] = [5, 9, 18, 27, 36, 45]
brackets[1996] = [1000, 4000, 8000]
rates[1996] = [10, 20, 30, 40]
brackets[2002] = [1000, 4000, 8000]
rates[2002] = [9, 18, 27, 36]
brackets[2005] = [1000, 4000, 8000]
rates[2005] = [8, 17, 26, 35]
brackets[2008] = [1200, 4600, 8800]
rates[2008] = [8, 17, 26, 35]
brackets[2009] = [1200, 4600, 8800]
rates[2009] = [6, 16, 25, 35]
brackets[2010] = [1200, 4600, 8800]
rates[2010] = [6, 15, 24, 35]
brackets[2012] = [1200, 4600, 8800, 30000]
rates[2012] = [6, 15, 24, 35, 38]
brackets[2014] = [1200, 4600, 8800, 15000]
rates[2014] = [6, 15, 24, 35, 38]
brackets[2017] = [1200, 4600, 8800, 15000, 50000]
rates[2017] = [6, 15, 24, 35, 38, 40]
brackets[2018] = [1200, 4600, 8800, 15000, 30000, 50000]
rates[2018] = [6, 15, 24, 35, 38, 40, 42]

def get_tax_year(year):
    tax_years = sorted(brackets)
    for i, tax_year in enumerate(tax_years):
        if i == len(tax_years) - 1:
            return tax_year
        if tax_year <= year < tax_years[i + 1]:
            return tax_year

def get_tax(year, income):
    tax_year = get_tax_year(year)
    bracket = brackets[tax_year]
    rate = rates[tax_year]
    tax = 0
    for i, current_bracket in enumerate(bracket):
        previous_bracket = bracket[i - 1] if i > 0 else 0
        if income <= current_bracket:
            tax += (income - previous_bracket) * rate[i] / 100
            break
        tax += (current_bracket - previous_bracket) * rate[i] / 100
        if i == len(bracket) - 1:
            tax += (income - current_bracket) * rate[i + 1] / 100
    return tax

income_year = 2020
years_to_plot = [1996, 2000, 2004, 2008, 2012, 2016, 2020]

import matplotlib.pyplot as plt

def plot():
    lines = []
    labels = []
    for year in years_to_plot:
        tax_year = get_tax_year(year)
        x = [0] + brackets[tax_year] + [100000]
        y = [get_tax(year, income) for income in x]
        f = get_price_level(income_year) / get_price_level(year)
        x = [income * f for income in x]
        y = [tax * f for tax in y]
        line, = plt.plot(x, y)
        label = f'{year}'
        lines.append(line)
        labels.append(label)
    return lines, labels

plt.figure(figsize=(12, 4))

plt.subplot(1, 3, 1)
plt.xlim(0, 5000)
plt.ylim(0, 1000)
lines, labels = plot()

plt.subplot(1, 3, 2)
plt.xlim(5000, 10000)
plt.ylim(500, 2500)
plot()

plt.subplot(1, 3, 3)
plt.xlim(10000, 15000)
plt.ylim(1500, 4500)
plot()

plt.figlegend(lines, labels, loc='lower center', ncol=len(labels))
plt.subplots_adjust(0.05, 0.15, 0.95, 0.95)
plt.savefig('tax.png')
