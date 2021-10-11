import jamotools

filename = "taocp"
data = []
with open(filename) as f:
    for line in f:
        hangul, latin = line.split()
        hangul = jamotools.split_syllables(hangul)
        latin = latin.lower()
        data.append((hangul, latin))

all_hangul = "ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ"
all_hangul += "ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅣㅢ"
assert len(all_hangul) == 35
all_latin = "abcdefghijklmnopqrstuvwxyz"
assert len(all_latin) == 26

pair = len(data)
sum_hangul = sum(len(hangul) for hangul, latin in data)
sum_latin = sum(len(latin) for hangul, latin in data)
max_hangul = max(len(hangul) for hangul, latin in data)
max_latin = max(len(latin) for hangul, latin in data)
avg_hangul = sum_hangul / pair
avg_latin = sum_latin / pair

print(f"{pair} name pairs")
print(f"{sum_hangul} Hangul letters (max {max_hangul} avg {avg_hangul:.2f})")
print(f"{sum_latin} Latin letters (max {max_latin} avg {avg_latin:.2f})")

from collections import Counter

hangul_counter = Counter()
latin_counter = Counter()
for hangul, latin in data:
    hangul_counter.update(hangul)
    latin_counter.update(latin)

part_blocks = [
    "",
    "\N{LEFT ONE EIGHTH BLOCK}",
    "\N{LEFT ONE QUARTER BLOCK}",
    "\N{LEFT THREE EIGHTHS BLOCK}",
    "\N{LEFT HALF BLOCK}",
    "\N{LEFT FIVE EIGHTHS BLOCK}",
    "\N{LEFT THREE QUARTERS BLOCK}",
    "\N{LEFT SEVEN EIGHTHS BLOCK}",
]

def block(number):
    whole = int(number)
    part = number - whole
    whole_block = "\N{FULL BLOCK}" * whole
    part_block = part_blocks[int(part * len(part_blocks))]
    return whole_block + part_block

for hangul in all_hangul:
    count = hangul_counter[hangul]
    bar = block(count / 8)
    print(f"{hangul:1} {bar} {count}")

for latin in all_latin:
    count = latin_counter[latin]
    bar = block(count / 8)
    print(f"{latin:2} {bar} {count}")
