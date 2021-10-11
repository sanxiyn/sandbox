import jamotools

filename = "test"
data = []
with open(filename) as f:
    for line in f:
        hangul, latin = line.split()
        data.append((hangul, latin))

all_hangul = "ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ"
all_hangul += "ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅣㅢ"
assert len(all_hangul) == 35
all_latin = "abcdefghijklmnopqrstuvwxyz"
assert len(all_latin) == 26

sequence_length = 15

def encode_with(letter_map, pad, length):
    def encode(word):
        tail = [pad] * (length - len(word))
        return list(letter_map[letter] for letter in word) + tail
    return encode

hangul_map = dict((letter, index) for index, letter in enumerate(all_hangul, 1))
latin_map = dict((letter, index) for index, letter in enumerate(all_latin, 1))
encode_hangul = encode_with(hangul_map, 0, sequence_length)
encode_latin = encode_with(latin_map, 0, sequence_length)

import numpy

def prepare_one(hangul, latin):
    hangul = jamotools.split_syllables(hangul)
    hangul = encode_hangul(hangul)
    hangul = numpy.array(hangul, numpy.int8)
    hangul = numpy.expand_dims(hangul, 0)
    latin = latin.lower()
    latin = encode_latin(latin)
    latin = numpy.array(latin, numpy.int8)
    latin = numpy.expand_dims(latin, 0)
    return [hangul, latin]

def prepare(data):
    hangul_sample = []
    latin_sample = []
    count = len(data)
    for i in range(count):
        for j in range(count):
            hangul = data[i][0]
            hangul = jamotools.split_syllables(hangul)
            hangul = encode_hangul(hangul)
            hangul_sample.append(hangul)
            latin = data[j][1]
            latin = latin.lower()
            latin = encode_latin(latin)
            latin_sample.append(latin)
    hangul_sample = numpy.array(hangul_sample, numpy.int8)
    latin_sample = numpy.array(latin_sample, numpy.int8)
    return [hangul_sample, latin_sample]

def plot(data):
    import matplotlib.pyplot as plt
    count = len(data)
    x = prepare(data)
    y = model.predict(x)
    v = y.reshape((count, count))
    ev = numpy.exp(v)
    p = ev / (ev + 1)
    plt.imshow(p)
    plt.savefig("matrix.png")

from tensorflow import keras

model = keras.models.load_model("model")
plot(data)
