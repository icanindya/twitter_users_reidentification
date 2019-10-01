# this file is modified from Richard Liao
import os
# import cPickle
import re

import numpy as np
import pandas as pd
from keras import backend as K
from keras import initializers
from keras.engine.topology import Layer
from keras.layers import Dense, Input
from keras.layers import Embedding, GRU, Bidirectional, TimeDistributed
from keras.models import Model
from keras.preprocessing.text import Tokenizer, text_to_word_sequence
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import LabelBinarizer

import helper

MAX_SENT_LENGTH = 100
MAX_SENTS = 15
MAX_NB_WORDS = 20000
EMBEDDING_DIM = 100
VALIDATION_SPLIT = 0.2

YEARLY_TWEETS_COMBINED_PATH = r'D:\Data\Linkage\FL\FL18\tweets\yearly_tweets_combined.csv'


def clean_str(string):
    """
    Tokenization/string cleaning for dataset
    Every dataset is lower cased except
    """

    string = re.sub(r"\\", "", string)
    string = re.sub(r"\'", "", string)
    string = re.sub(r"\"", "", string)
    return string.strip().lower()


input_ds_path = YEARLY_TWEETS_COMBINED_PATH
input_col_names = ['twitter_id', 'doc', 'dob_or_age', 'sex', 'race_code', 'zip_code', 'city', 'party']

data_train = pd.read_csv(input_ds_path, encoding='utf-8', names=input_col_names, nrows=30000)
print(data_train.shape)

from nltk import tokenize

doc = []
labels = []
texts = []

for idx in range(data_train.doc.shape[0]):
    text = data_train.doc[idx]
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    text = clean_str(text)
    texts.append(text)
    sentences = tokenize.sent_tokenize(text)
    doc.append(sentences)

    age = data_train.dob_or_age[idx]
    labels.append(helper.get_maif_age_label(age))

tokenizer = Tokenizer(num_words=MAX_NB_WORDS)
tokenizer.fit_on_texts(texts)

data = np.zeros((len(texts), MAX_SENTS, MAX_SENT_LENGTH), dtype='int32')

for i, sentences in enumerate(doc):
    for j, sent in enumerate(sentences):
        if j < MAX_SENTS:
            wordTokens = text_to_word_sequence(sent)
            k = 0
            for _, word in enumerate(wordTokens):
                if k < MAX_SENT_LENGTH and tokenizer.word_index[word] < MAX_NB_WORDS:
                    data[i, j, k] = tokenizer.word_index[word]
                    k = k + 1

word_index = tokenizer.word_index
print('Total %s unique tokens.' % len(word_index))

# labels = to_categorical(np.asarray(labels))

labels = np.array(labels)
unique_labels = np.unique(labels)
num_labels = len(unique_labels)

print('Shape of data tensor:', data.shape)
print('Shape of label tensor:', labels.shape)

indices = np.arange(data.shape[0])
np.random.shuffle(indices)
data = data[indices]
labels = labels[indices]

label_binerizer = LabelBinarizer()
enc_labels = label_binerizer.fit_transform(labels)

nb_validation_samples = int(VALIDATION_SPLIT * data.shape[0])

X_train = data[:-nb_validation_samples]
y_train = enc_labels[:-nb_validation_samples]
X_test = data[-nb_validation_samples:]
y_test = enc_labels[-nb_validation_samples:]

print('Number of positive and negative doc in traing and validation set')
print(y_train.sum(axis=0))
print(y_test.sum(axis=0))

GLOVE_DIR = "D:\Data\glove.6B"
embeddings_index = {}
f = open(os.path.join(GLOVE_DIR, 'glove.6B.100d.txt'), encoding='utf-8')
for line in f:
    values = line.split()
    word = values[0]
    coefs = np.asarray(values[1:], dtype='float32')
    embeddings_index[word] = coefs
f.close()

print('Total %s word vectors.' % len(embeddings_index))

embedding_matrix = np.random.random((len(word_index) + 1, EMBEDDING_DIM))
for word, i in word_index.items():
    embedding_vector = embeddings_index.get(word)
    if embedding_vector is not None:
        # words not found in embedding index will be all-zeros.
        embedding_matrix[i] = embedding_vector

# building Hierachical Attention network
embedding_matrix = np.random.random((len(word_index) + 1, EMBEDDING_DIM))
for word, i in word_index.items():
    embedding_vector = embeddings_index.get(word)
    if embedding_vector is not None:
        # words not found in embedding index will be all-zeros.
        embedding_matrix[i] = embedding_vector

embedding_layer = Embedding(len(word_index) + 1,
                            EMBEDDING_DIM,
                            weights=[embedding_matrix],
                            input_length=MAX_SENT_LENGTH,
                            trainable=True,
                            mask_zero=True)


class AttLayer(Layer):
    def __init__(self, attention_dim):
        self.init = initializers.get('normal')
        self.supports_masking = True
        self.attention_dim = attention_dim
        super(AttLayer, self).__init__()

    def build(self, input_shape):
        assert len(input_shape) == 3
        self.W = K.variable(self.init((input_shape[-1], self.attention_dim)), name='W')
        self.b = K.variable(self.init((self.attention_dim,)), name='b')
        self.u = K.variable(self.init((self.attention_dim, 1)), name='u')
        self.trainable_weights = [self.W, self.b, self.u]
        super(AttLayer, self).build(input_shape)

    def compute_mask(self, inputs, mask=None):
        return None

    def call(self, x, mask=None):
        # size of x :[batch_size, sel_len, attention_dim]
        # size of u :[batch_size, attention_dim]
        # uit = tanh(xW+b)
        uit = K.tanh(K.bias_add(K.dot(x, self.W), self.b))
        ait = K.dot(uit, self.u)
        ait = K.squeeze(ait, -1)

        ait = K.exp(ait)

        if mask is not None:
            # Cast the mask to floatX to avoid float64 upcasting in theano
            ait *= K.cast(mask, K.floatx())
        ait /= K.cast(K.sum(ait, axis=1, keepdims=True) + K.epsilon(), K.floatx())
        ait = K.expand_dims(ait)
        weighted_input = x * ait
        output = K.sum(weighted_input, axis=1)

        return output

    def compute_output_shape(self, input_shape):
        return (input_shape[0], input_shape[-1])


sentence_input = Input(shape=(MAX_SENT_LENGTH,), dtype='int32')
embedded_sequences = embedding_layer(sentence_input)
l_lstm = Bidirectional(GRU(100, return_sequences=True))(embedded_sequences)
l_att = AttLayer(100)(l_lstm)
sentEncoder = Model(sentence_input, l_att)

review_input = Input(shape=(MAX_SENTS, MAX_SENT_LENGTH), dtype='int32')
review_encoder = TimeDistributed(sentEncoder)(review_input)
l_lstm_sent = Bidirectional(GRU(100, return_sequences=True))(review_encoder)
l_att_sent = AttLayer(100)(l_lstm_sent)
preds = Dense(num_labels, activation='softmax')(l_att_sent)
model = Model(review_input, preds)

model.compile(loss='categorical_crossentropy',
              optimizer='rmsprop',
              metrics=['accuracy'])

print("model fitting - Hierachical attention network")
model.fit(X_train, y_train, validation_data=(X_test, y_test),
          epochs=20, batch_size=100)

scores = model.evaluate(X_test, y_test)

y_pred = model.predict(X_test)
y_pred_orig = label_binerizer.inverse_transform(y_pred)
y_test_orig = label_binerizer.inverse_transform(y_test)

cm = confusion_matrix(y_test_orig, y_pred_orig, labels=unique_labels)
cm_df = pd.DataFrame(cm, index=unique_labels, columns=unique_labels)

print('{}: {:.2f}'.format(model.metrics_names[1], scores[1] * 100) + '\n')
print(str(cm_df) + '\n')
