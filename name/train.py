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

def word_of(letter_set):
    def predicate(word):
        return all(letter in letter_set for letter in word)
    return predicate

hangul_set = set(all_hangul)
latin_set = set(all_latin)
is_hangul = word_of(hangul_set)
is_latin = word_of(latin_set)
assert all(is_hangul(hangul) for hangul, latin in data)
assert all(is_latin(latin) for hangul, latin in data)

from tensorflow import keras
from tensorflow.keras import layers

sequence_length = 15
embedding_dim = 50
hidden_dim = 12

hangul_input = keras.Input(shape=(sequence_length,), dtype="int8")
latin_input = keras.Input(shape=(sequence_length,), dtype="int8")
hangul_embed = layers.Embedding(len(all_hangul) + 1, embedding_dim)
latin_embed = layers.Embedding(len(all_latin) + 1, embedding_dim)
hangul_embedded = hangul_embed(hangul_input)
latin_embedded = latin_embed(latin_input)
gru_encode = layers.GRU(hidden_dim, return_sequences=True)
hangul_encoded = gru_encode(hangul_embedded)
latin_encoded = gru_encode(latin_embedded)
attend = layers.Attention()
attended = attend([hangul_encoded, latin_encoded])
pool = layers.GlobalAveragePooling1D()
pooled = pool(attended)
predict = layers.Dense(1)
output = predict(pooled)

model = keras.Model(inputs=[hangul_input, latin_input], outputs=[output])
optimizer = keras.optimizers.Adam()
loss = keras.losses.BinaryCrossentropy(from_logits=True)
accuracy = keras.metrics.BinaryAccuracy(threshold=0)
model.compile(optimizer=optimizer, loss=loss, metrics=[accuracy])

def encode_with(letter_map, pad, length):
    def encode(word):
        tail = [pad] * (length - len(word))
        return list(letter_map[letter] for letter in word) + tail
    return encode

hangul_map = dict((letter, index) for index, letter in enumerate(all_hangul, 1))
latin_map = dict((letter, index) for index, letter in enumerate(all_latin, 1))
encode_hangul = encode_with(hangul_map, 0, sequence_length)
encode_latin = encode_with(latin_map, 0, sequence_length)

encoded_data = []
for hangul, latin in data:
    encoded_hangul = encode_hangul(hangul)
    encoded_latin = encode_latin(latin)
    encoded_data.append((encoded_hangul, encoded_latin))

def sample(count):
    for i in range(count):
        for _ in range(count):
            yield i, i
        for j in range(count):
            yield i, j

def judge(data, i, j):
    hangul_i, latin_i = data[i]
    hangul_j, latin_j = data[j]
    if hangul_i == hangul_j or latin_i == latin_j:
        return 1
    return 0

import random

import numpy

def generate():
    hangul_sample = []
    latin_sample = []
    label_sample = []
    count = len(data)
    sampled = sample(count)
    sampled = list(sampled)
    random.shuffle(sampled)
    for i, j in sampled:
        encoded_hangul = encoded_data[i][0]
        encoded_latin = encoded_data[j][1]
        label = judge(data, i, j)
        hangul_sample.append(encoded_hangul)
        latin_sample.append(encoded_latin)
        label_sample.append(label)
    hangul_sample = numpy.array(hangul_sample, numpy.int8)
    latin_sample = numpy.array(latin_sample, numpy.int8)
    label_sample = numpy.array(label_sample, numpy.int8)
    return [hangul_sample, latin_sample], label_sample

def lr_schedule(epoch, lr):
    if epoch in [10, 20]:
        return lr * 0.5
    return lr

def train():
    x, y = generate()
    stop = keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True)
    schedule = keras.callbacks.LearningRateScheduler(lr_schedule)
    show = keras.callbacks.TensorBoard()
    cb = [stop, schedule, show]
    history = model.fit(x, y, epochs=100, callbacks=cb, validation_split=0.1)
    return history

def plot(history):
    import matplotlib.pyplot as plt
    plt.plot(history.history["binary_accuracy"], color="red")
    plt.plot(history.history["val_binary_accuracy"], color="blue")
    plt.savefig("history.png")

history = train()
plot(history)
model.save("model")
