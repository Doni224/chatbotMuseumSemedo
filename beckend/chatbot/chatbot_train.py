# libraries
import random
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.optimizers import schedules
from keras.layers import Dense, Dropout
from keras.models import load_model
from keras.models import Sequential
import numpy as np
import pickle
import json
import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

nltk.download("punkt")
nltk.download("wordnet")

# init file
words = []
classes = []
documents = []
ignore_words = ["?", "!"]
data_file = open("intents.json").read()
intents = json.loads(data_file)

for intent in intents["intents"]:
  #membaca pola
    for pattern in intent["patterns"]:

        #memecah setiap pola menjadi token-token kata, yang kemudian disimpan dalam variabel "w"
        w = nltk.word_tokenize(pattern)
        words.extend(w)
        # adding documents
        documents.append((w, intent["tag"]))

        # menambahkan setiap tag "intent" ke dalam daftar kelas "classes"
        if intent["tag"] not in classes:
            classes.append(intent["tag"])

words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]
words = sorted(list(set(words)))

classes = sorted(list(set(classes)))

print(len(documents), "documents")

print(len(classes), "classes", classes)

print(len(words), "unique lemmatized words", words)


pickle.dump(words, open("words.pkl", "wb"))
pickle.dump(classes, open("classes.pkl", "wb"))

# initializing training data
training = []
output_empty = [0] * len(classes)
for doc in documents:
    # menginisialisasi sekumpulan kata
    bag = []
    #daftar kata-kata yang telah dipisahkan menjadi token untuk pola
    pattern_words = doc[0]
    #lemmatize mengubah huruf besar menjadi huruf kecil
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]
    # mengecek kata jika ada akan tambah nilai 1, jika tidak ada nilai 0
    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)

    # nilai awal adalah list output_empty yang berisi nilai 0 sebanyak jumlah kelas diubah 1 untuk menandakan kelas dari kalimat
    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1
#Setiap bag dan output_row ditambahkan ke dalam training sebagai data latih.
    training.append([bag, output_row])


# shuffle our features and turn into np.array
random.shuffle(training)
training = np.array(training, dtype=object)

# create train and test lists. X - patterns, Y - intents
train_x = list(training[:, 0])
train_y = list(training[:, 1])

print("Training data created")


model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation="relu"))
model.add(Dropout(0.5))
model.add(Dense(64, activation="relu"))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation="softmax"))
model.summary()
# mengurangi learning rate
lr_schedule = schedules.ExponentialDecay(
    initial_learning_rate=0.01,
    decay_steps=10000,
    decay_rate=0.96,
    staircase=True)
sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss="categorical_crossentropy", optimizer=sgd, metrics=["accuracy"])

from keras import callbacks
earlystopping = callbacks.EarlyStopping(monitor ="loss", mode ="min", patience = 5, restore_best_weights = True)
callbacks =[earlystopping]

hist = model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1)
model.save("chatbot_model.h5", hist)
print("model created")

