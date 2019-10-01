import numpy as np
import pandas as pd
import tensorflow as tf
from keras.layers import Conv1D, BatchNormalization, Activation
from keras.layers import Embedding, Input, Dense, Dropout, Lambda, MaxPooling1D
from keras.models import Model
from keras.models import Sequential
from keras.optimizers import SGD
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer

import helper

YEARLY_TWEETS_COMBINED_PATH = r'D:\Data\Linkage\FL\FL18\tweets\yearly_tweets_combined.csv'
ALL_TWEETS_COMBINED_PATH = r'D:\Data\Linkage\FL\FL18\tweets\all_tweets_combined.csv'
input_col_names = ['twitter_id', 'doc', 'dob_or_age', 'sex', 'race_code', 'zip_code', 'city', 'party']

ALPHABET = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-', ',', ';',
            '.', '!', '?', ':', '’', '"', '/', '|', '_', '#', '$', '%', 'ˆ',
            '&', '*', '˜', '‘', '+', '=', '<', '>', '(', ')', '[', ']', '{',
            '}', ' ']

FEATURE_LEN = 1024
EMBEDDING_SIZE = 16
TOP_K_VAL = 3
ALPHABET = ALPHABET  # + helper.UPPERCASE_ALPHABET + helper.EXTENDED_ALPHABET

print(ALPHABET)

char_dict = {}
for i, c in enumerate(ALPHABET):
    char_dict[c] = i + 1


def text_to_int_arr(text, max_length=FEATURE_LEN):
    #    text = text.lower()

    int_arr = np.zeros(max_length)

    for i in range(0, len(text)):
        if i >= max_length:
            return int_arr

        elif text[i] in char_dict:
            int_arr[i] = char_dict[text[i]]

        else:
            int_arr[i] = len(ALPHABET) + 1

    return int_arr


def conv_shape(conv):
    return conv.get_shape().as_list()[1:]


def ConvolutionalBlock(input_shape, num_filters):
    model = Sequential()

    # 1st conv layer
    model.add(Conv1D(filters=num_filters, kernel_size=3, strides=1, padding="same", input_shape=input_shape))
    model.add(BatchNormalization())
    model.add(Activation("relu"))

    # 2nd conv layer
    model.add(Conv1D(filters=num_filters, kernel_size=3, strides=1, padding="same"))
    model.add(BatchNormalization())
    model.add(Activation("relu"))

    return model


def vdcnn_model(num_filters, num_classes, sequence_max_length, num_chars, embedding_size, top_k_val,
                learning_rate=0.001):
    inputs = Input(shape=(sequence_max_length,), dtype='int32', name='input')

    embedded_seq = Embedding(num_chars, embedding_size, input_length=sequence_max_length)(inputs)

    embedded_seq = BatchNormalization()(embedded_seq)

    # 1st Layer
    conv = Conv1D(filters=64, kernel_size=3, strides=2, padding="same")(embedded_seq)

    # ConvBlocks
    for i in range(len(num_filters)):
        conv = ConvolutionalBlock(conv_shape(conv), num_filters[i])(conv)
        conv = MaxPooling1D(pool_size=3, strides=2, padding="same")(conv)

    def _top_k(x):
        x = tf.transpose(x, [0, 2, 1])
        k_max = tf.nn.top_k(x, k=top_k_val)
        return tf.reshape(k_max[0], (-1, num_filters[-1] * top_k_val))

    k_max = Lambda(_top_k, output_shape=(num_filters[-1] * top_k_val,))(conv)

    # fully connected layers
    # in original paper they didn't used dropouts
    fc1 = Dense(512, activation='relu', kernel_initializer='he_normal')(k_max)
    fc1 = Dropout(0.3)(fc1)
    fc2 = Dense(512, activation='relu', kernel_initializer='he_normal')(fc1)
    fc2 = Dropout(0.3)(fc2)
    out = Dense(num_classes, activation='softmax')(fc2)

    # optimizer
    sgd = SGD(lr=learning_rate, decay=1e-6, momentum=0.9, nesterov=False)

    model = Model(inputs=inputs, outputs=out)
    model.compile(optimizer=sgd, loss='categorical_crossentropy', metrics=['accuracy'])

    return model


num_filters = [64, 128, 256, 512]

input_ds_path = YEARLY_TWEETS_COMBINED_PATH
df = pd.read_csv(input_ds_path, encoding='utf-8', names=input_col_names)

X = np.array([text_to_int_arr(x) for x in df['doc'].values])
y = df['dob_or_age'].map(lambda x: helper.get_maif_age_label(x)).values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)

label_binerizer = LabelBinarizer()
label_binerizer.fit(y)
labels = label_binerizer.classes_

y_train = label_binerizer.transform(y_train)
y_test = label_binerizer.transform(y_test)

model = vdcnn_model(num_filters=num_filters,
                    num_classes=len(labels),
                    num_chars=len(ALPHABET) + 1,
                    sequence_max_length=FEATURE_LEN,
                    embedding_size=EMBEDDING_SIZE,
                    top_k_val=TOP_K_VAL)

model.summary()

model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=50, batch_size=128)
scores = model.evaluate(X_test, y_test)
y_pred = model.predict(X_test)

y_pred_orig = label_binerizer.inverse_transform(y_pred)
y_test_orig = label_binerizer.inverse_transform(y_test)

cm = confusion_matrix(y_test_orig, y_pred_orig, labels=labels)
cm_df = pd.DataFrame(cm, index=labels, columns=labels)

print('{}: {:.2f}'.format(model.metrics_names[1], scores[1] * 100) + '\n')
print(str(cm_df) + '\n')
