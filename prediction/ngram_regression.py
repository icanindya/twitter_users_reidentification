import sys

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import Lasso
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split

import helper

YEARLY_TWEETS_COMBINED_PATH = r'D:\Data\Linkage\FL\FL18\tweets\yearly_tweets_combined.csv'
input_col_names = ['twitter_id', 'doc', 'dob_or_age', 'sex', 'race_code', 'zip_code', 'city', 'party']

N = 1
MAX = 5000
CUSTOM_TFIDF = 0
count = 0

y = []

data_size = 0
vocabulary = []


def text_processor(text):
    global count
    count += 1
    if count % 1000 == 0:
        print('count: {}'.format(count))

    tokens = text.split('\t')
    age = int(tokens[-1])
    if len(y) != data_size:
        y.append(age)
    elif y[count - 1] != age:
        print('error')
    return tokens[:-1]


def fit_custom_tfidf(rows):
    vectorizer = CountVectorizer(analyzer=text_processor, vocabulary=vocabulary)
    rows = vectorizer.fit_transform(rows)
    rows = rows.todense()
    #    print(rows)

    idf = np.log2(rows.shape[0] / np.count_nonzero(rows, axis=0))
    #    print(idf)

    tf = 0.5 + 0.5 * (rows / (np.amax(rows, axis=1) + 0.0001))
    #    print(tf)

    tfidf = np.multiply(tf, idf)

    return tfidf


def fit_tfidf(rows):
    vectorizer = TfidfVectorizer(analyzer=text_processor, vocabulary=vocabulary)
    tfidf = vectorizer.fit_transform(rows)
    tfidf = tfidf.todense()

    return tfidf


input_ds_path = YEARLY_TWEETS_COMBINED_PATH

top_onegrams = open(r"D:\top_onegrams_6702746.txt", 'r', encoding='utf-8').read().splitlines()[:MAX]
top_twograms = open(r"D:\top_twograms_70989637.txt", 'r', encoding='utf-8').read().splitlines()[:MAX]

top_ngrams = {1: top_onegrams, 2: top_twograms}

feature_mat = None

for n in [1, 2]:

    rows = []

    vocabulary = top_ngrams[n]

    with open(r"D:\{}grams_label.txt".format(n), 'r', encoding='utf-8') as rf:
        for i, line in enumerate(rf):
            rows.append(line.rstrip())
    count = 0

    data_size = len(rows)

    tfidf = fit_tfidf(rows)

    if feature_mat is None:
        feature_mat = tfidf
    else:
        feature_mat = np.concatenate((feature_mat, tfidf), axis=1)

X = feature_mat

print(X.shape)

if len(sys.argv) > 1:
    CUSTOM_TFIDF = int(sys.argv[1])

X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)

clf = Lasso(alpha=0.001)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
y_test = list(map(lambda age: helper.get_maif_age_label(age), y_test))
y_pred = list(map(lambda age: helper.get_maif_age_label(age), y_pred))
acc = accuracy_score(y_test, y_pred)
labels = list(set(y_test + y_pred))

cm = confusion_matrix(y_test, y_pred, labels=labels)
cm_df = pd.DataFrame(cm, index=labels, columns=labels)

print('acc: {}'.format(acc))
print(cm_df)
