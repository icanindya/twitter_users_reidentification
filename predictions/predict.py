import pandas as pd
import numpy as np
import sys
import os
import re

import helper
from sklearn.decomposition import PCA
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelBinarizer, StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from keras.layers import Dense
from keras.models import Sequential
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.ensemble import RandomForestClassifier
import csv
from nltk.stem import PorterStemmer
from nltk.util import ngrams
import joblib
from keras.optimizers import SGD, Adam, RMSprop
from keras.preprocessing.text import Tokenizer, text_to_word_sequence
from sklearn.feature_extraction.text import CountVectorizer
import unidecode

sys.path.append(r'D:\Projects\Python\AttributePrediction\thirdparty_modules\VDCNN')
from vdcnn import VDCNN
from HAN import HAN

ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv'
YEARLY_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\yearly_tweets.csv'
NUM_TWEETS = 50
SELECTED_TWITTER_IDS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\twitter_ids_{}_tweets.csv'.format(NUM_TWEETS)
PREDICTION_PATH = r'D:\Data\Linkage\FL\FL18\attributes\predictions\{}_{}_{}.csv'
MODEL_PATH = r'D:\Data\Linkage\FL\FL18\attributes\models\{}_{}_{}.model'

TOP_1GRAMS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\top_1grams.txt'
TOP_2GRAMS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\top_2grams.txt'

porter_stemmer = PorterStemmer()

SAVE_RESULTS = True
SAVE_PREDICTIONS = True


def preprocess_name(name):

    # Remove parethesized content
    name = name.replace(r'\(.*\)', '')

    # Convert accented characters
    name = unidecode.unidecode(name)

    # Replace '-', '_' and '.' with ' ':
    name = name.replace('-', ' ').replace('_', ' ').replace('.', ' ')

    # Remove non-alpha characters except spaces
    name = re.sub(r'[^a-zA-Z ]', '', name)

    # Make lower-case
    name = name.lower()

    # Remove prefix mr., mr , ms , ms., mrs., mrs , miss, sir, dr
    prefix_list = ['mr ', 'ms ', 'mrs ', 'miss ', 'sir ', 'dr ']

    for prefix in prefix_list:
        if name.startswith(prefix):
            name = name[len(prefix):]

    # Convert consecutive spaces into single space
    name = re.sub(' +', ' ', name)

    # Finally trim
    name = name.strip()

    return name


def process_text(row):

    text = row[0]
    tokens_lower = [x.lower() for x in text.split() if not helper.stop_mention_url_or_symbol(x)]
    stems = [porter_stemmer.stem(token) for token in tokens_lower]
    onegrams = [' '.join(ngram) for ngram in ngrams(stems, 1)]
    twograms = [' '.join(ngram) for ngram in ngrams(stems, 2)]

    return onegrams + twograms


def  han_model(X_train, y_train, X_test, y_test,
               output_shape, max_sents, max_sent_length, word_index_len, embedding_dim, embedding_matrix):

    model = HAN(output_shape, max_sents, max_sent_length, word_index_len, embedding_dim, embedding_matrix)

    if y_train.shape[1] == 1:
        model.compile(loss='binary_crossentropy', optimizer=RMSprop(lr=0.0001), metrics=['accuracy'])
    else:
        model.compile(loss='categorical_crossentropy', optimizer=RMSprop(lr=0.0001), metrics=['accuracy'])

    model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=50, batch_size=128)

    scores = model.evaluate(X_test, y_test)
    accuracy = scores[1] * 100
    y_pred = model.predict(X_test)

    return accuracy, y_pred


def vdcnn_model(X_train, y_train, X_test, y_test, sequence_max_length):

    model = VDCNN(num_classes=y_train.shape[1], sequence_length=sequence_max_length)

    if y_train.shape[1] == 1:
        model.compile(loss='binary_crossentropy', optimizer=SGD(lr=0.0001, momentum=0.9), metrics=['accuracy'])
    else:
        model.compile(loss='categorical_crossentropy', optimizer=SGD(lr=0.0001, momentum=0.9), metrics=['accuracy'])

    model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=50, batch_size=128)

    scores = model.evaluate(X_test, y_test)
    accuracy = scores[1] * 100
    y_pred = model.predict(X_test)

    return accuracy, y_pred


def neural_net(X_train, y_train, X_test, y_test, hidden_len):

    hidden_dim = (X_train.shape[1] + y_train.shape[1]) // 2

    model = Sequential()
    model.add(Dense(hidden_dim, activation='relu', input_dim=X_train.shape[1]))
    for i in range(hidden_len):
        model.add(Dense(hidden_dim, activation='relu'))

    if y_train.shape[1] == 1:
        model.add(Dense(y_train.shape[1], activation='sigmoid'))
        model.compile(loss='binary_crossentropy', optimizer=Adam(lr=0.0001), metrics=['accuracy'])
    else:
        model.add(Dense(y_train.shape[1], activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer=Adam(lr=0.0001), metrics=['accuracy'])
    model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=100, batch_size=128)

    scores = model.evaluate(X_test, y_test)
    accuracy = scores[1] * 100
    y_pred = model.predict(X_test)

    y_pred_proba = model.predict_proba(X_test)

    return model, accuracy, y_pred, y_pred_proba


def svm(X_train, y_train, X_test, y_test):
    model = OneVsRestClassifier(SVC())
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred) * 100

    return accuracy, y_pred


def logistic(X_train, y_train, X_test, y_test):

    model = LogisticRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred) * 100

    return accuracy, y_pred

def random_forest(X_train, y_train, X_test, y_test):

    model = RandomForestClassifier(n_estimators=1000, max_depth=None, random_state=helper.random_seed)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred) * 100

    return accuracy, y_pred


def save_model_predictions(attribute, algo, features, model, labels, test_twitter_ids, test_actuals, test_preds, pred_probs):

    if len(labels) == 2:
        labels = ['prob']

    with open(MODEL_PATH.format(attribute, algo, '-'.join(features)), 'w', newline='', encoding='utf-8') as json_file:
        json_file.write(model.to_json())

    with open(PREDICTION_PATH.format(attribute, algo, '-'.join(features)), 'w', newline='', encoding='utf-8') as wf:
        csv_writer = csv.writer(wf, delimiter=',')

        csv_writer.writerow(['twitter_id', 'orig_{}'.format(attribute), 'pred_{}'.format(attribute)] + list(labels))

        for id, actual, pred, prob in zip(test_twitter_ids, test_actuals, test_preds, pred_probs):
            csv_writer.writerow([str(id), actual, pred] + list(prob))

if len(sys.argv) > 1:
    attribute_list = [sys.argv[1]]
    algo_list = [sys.argv[2]]
    features = []
    for i in range(3, len(sys.argv)):
        features.append(sys.argv[i])
    features_list = [features]

else:
    attribute_list = ['sex']
    algo_list = ['nn']
    features_list = [['doc2vec', 'name_ngrams']]

ids_df = pd.read_csv(SELECTED_TWITTER_IDS_PATH, header=0)
test_ids_df = ids_df.sample(frac=helper.test_percentage, random_state=helper.random_seed)
test_ids = test_ids_df['twitter_id'].tolist()
train_ids_df = ids_df.drop(test_ids_df.index)
train_ids = train_ids_df['twitter_id'].tolist()

tokenizer = None

with open(r'D:\Data\Linkage\FL\FL18\attributes\results_varying_rows.txt', 'a', encoding='utf-8') as wf:
    for features in features_list:
        for algo in algo_list:
            for attribute in attribute_list:

                print('attribute: {} | features: {} | algorithm: {}'.format(attribute, ','.join(features), algo))

                df_list = []

                dataset_path = ALL_TWEETS_PATH
                df = pd.read_csv(dataset_path, header=0, usecols=['twitter_id', attribute])
                if attribute == 'race':
                    df['race'] = df['race'].apply(helper.get_short_race)
                elif attribute == 'dob':
                    df['dob'] = df['dob'].apply(helper.get_generation)
                elif attribute == 'party':
                    df['party'] = df['party'].apply(helper.get_short_party)

                df_list.append(df)

                file_name, file_ext = os.path.splitext(dataset_path)

                if 'glove' in features:
                    features_path = file_name + '_glove_100_features.csv'
                    df_list.append(pd.read_csv(features_path, header=0))

                if 'fasttext' in features:
                    features_path = file_name + '_fb_ftext_100_features.csv'
                    df_list.append(pd.read_csv(features_path, header=0))

                if 'doc2vec' in features:
                    features_path = file_name + '_d2v_100_features.csv'
                    # features_path = file_name + '_chunked_d2v_100_features_{}_tweets.csv'.format(num_tweets)
                    df_list.append(pd.read_csv(features_path, header=0))

                if 'linguistic' in features:
                    features_path = file_name + '_linguistic_features.csv'
                    df_list.append(pd.read_csv(features_path, header=0))

                if 'lda' in features:
                    features_path = file_name + '_lda_60_doc_features.csv'
                    df_list.append(pd.read_csv(features_path, header=0))

                if 'empath' in features:
                    features_path = file_name + '_empath_194_features.csv'
                    df_list.append(pd.read_csv(features_path, header=0))

                if 'name_ngrams' in features:

                    features_path = file_name + '_twitter_name_handle.csv'
                    twitter_name_df = pd.read_csv(features_path, header=0, usecols=['twitter_name'],
                                          converters={'twitter_name': str})

                    twitter_name_df['twitter_name'] = twitter_name_df['twitter_name'].apply(preprocess_name)
                    vect = TfidfVectorizer(analyzer='char', max_df=0.3, min_df=3, ngram_range=(2, 2), lowercase=False)
                    name_ngrams_tfidf = vect.fit_transform(twitter_name_df['twitter_name'])

                    print(len(vect.get_feature_names()))

                    df_list.append(pd.DataFrame(name_ngrams_tfidf.todense()))

                if 'twitter_handle' in features:
                    features_path = file_name + '_twitter_handle.csv'
                    df_list.append(pd.read_csv(features_path, header=0))

                if 'text' in features:
                    features_path = file_name + '_tokens.csv'
                    tokens_df = pd.read_csv(features_path, header=0)
                    tokens_df['tokens_joined'] = tokens_df['tokens_joined'].apply(
                        lambda text: ' '.join([tok.lower() for tok in text.split() if not helper.stop_or_mention(tok)])
                    )
                    df_list.append(tokens_df)

                if 'ngrams' in features:
                    model_path = file_name + '_tfidf_20000.model'
                    tfidf = joblib.load(model_path)
                    tfidf_dense = tfidf.todense()
                    df_list.append(pd.DataFrame(tfidf_dense))

                df = pd.concat(df_list, axis=1)

                train_df = df.loc[df['twitter_id'].isin(train_ids)]
                test_df = df.loc[df['twitter_id'].isin(test_ids)]

                test_twitter_ids = test_df['twitter_id'].tolist()

                X_train = train_df.drop(['twitter_id', attribute], axis=1).values
                y_train = np.array(train_df[attribute])
                X_test = test_df.drop(['twitter_id', attribute], axis=1).values
                y_test = np.array(test_df[attribute])

                if 'text' not in features:
                    scaler = StandardScaler()
                    X_train = scaler.fit_transform(X_train)
                    X_test = scaler.transform(X_test)
                    # pca = PCA(n_components=100)
                    # X_train =  pca.fit_transform(X_train)
                    # X_test = pca.transform(X_test)

                y = np.concatenate((y_train, y_test))
                label_binerizer = LabelBinarizer().fit(y)
                y_train = label_binerizer.transform(y_train)
                y_test = label_binerizer.transform(y_test)
                y_test_inv = label_binerizer.inverse_transform(y_test)

                if algo == 'nn':
                    model, accuracy, y_pred, y_pred_proba = neural_net(X_train, y_train, X_test, y_test, hidden_len=1)

                elif algo == 'svm':
                    accuracy, y_pred = svm(X_train, y_train, X_test, y_test)

                elif algo == 'han':

                    MAX_SENT_LENGTH = 100
                    MAX_SENTS = 15
                    MAX_NB_WORDS = 20000
                    EMBEDDING_DIM = 100

                    if not tokenizer:

                        docs = [row[0] for row in X_train.tolist() + X_test.tolist()]
                        tokenizer = Tokenizer(num_words=MAX_NB_WORDS)
                        tokenizer.fit_on_texts(docs)

                    word_index = tokenizer.word_index
                    print('Total %s unique tokens.' % len(word_index))

                    def doc2tensor(row):

                        doc = row[0]

                        sentences = doc.lower().split()

                        data = np.zeros((MAX_SENTS, MAX_SENT_LENGTH), dtype='int32')

                        for j, sent in enumerate(sentences):
                            if j < MAX_SENTS:
                                wordTokens = text_to_word_sequence(sent)
                                k = 0
                                for _, word in enumerate(wordTokens):
                                    if k < MAX_SENT_LENGTH and tokenizer.word_index[word] < MAX_NB_WORDS:
                                        data[j, k] = tokenizer.word_index[word]
                                        k = k + 1

                        return data

                    X_train = np.apply_along_axis(doc2tensor, 1, X_train)
                    X_test = np.apply_along_axis(doc2tensor, 1, X_test)

                    GLOVE_PRETRAINED_MODEL_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\glove.twitter.27B.100d.txt'
                    embeddings_index = {}
                    f = open(GLOVE_PRETRAINED_MODEL_PATH, encoding='utf-8')
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

                    accuracy, y_pred = han_model(X_train, y_train, X_test, y_test,
                                                 y_train.shape[1], MAX_SENTS, MAX_SENT_LENGTH, len(word_index), EMBEDDING_DIM, embedding_matrix)

                elif algo == 'vdcnn':

                    alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789-,;.!?:’"/|_#$%ˆ&*˜‘+=<>()[]{} '
                    char_dict = {}
                    sequence_max_length = 1024
                    for i, c in enumerate(alphabet):
                        char_dict[c] = i + 1

                    def char2vec(row):
                        text = row[0]

                        data = np.zeros(sequence_max_length)
                        for i in range(0, len(text)):
                            if i >= sequence_max_length:
                                return data
                            elif text[i] in char_dict:
                                data[i] = char_dict[text[i]]
                            else:
                                # unknown character set to be 68
                                data[i] = 68
                        return data

                    X_train = np.apply_along_axis(char2vec, 1, X_train)
                    X_test = np.apply_along_axis(char2vec, 1, X_test)

                    accuracy, y_pred = vdcnn_model(X_train, y_train, X_test, y_test, sequence_max_length=sequence_max_length)

                elif algo == 'rf':
                    accuracy, y_pred = random_forest(X_train, y_train, X_test, y_test)

                elif algo == 'logistic':
                    accuracy, y_pred = random_forest(X_train, y_train, X_test, y_test)

                y_pred_inv = label_binerizer.inverse_transform(y_pred)

                cm = confusion_matrix(y_test_inv, y_pred_inv, labels=label_binerizer.classes_)
                cm_df = pd.DataFrame(cm, index=label_binerizer.classes_, columns=label_binerizer.classes_)
                cm_df.sort_index(axis=1, inplace=True)

                # print('attribute: {} | features: {} | algorithm: {}\n'.format(attribute, ','.join(features), algo))
                print('accuracy: {:.2f}\n'.format(accuracy))
                print('confusion matrix:\n')
                with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                    print('{}\n\n'.format(str(cm_df)))


                if SAVE_RESULTS:

                    wf.write('attribute: {} | features: {} | algorithm: {}\n'.format(attribute, ','.join(features), algo))
                    wf.write('accuracy: {:.2f}\n'.format(accuracy))
                    wf.write('confusion matrix:\n')
                    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                        wf.write('{}\n\n'.format(str(cm_df)))
                    wf.flush()

                if SAVE_PREDICTIONS:

                    save_model_predictions(attribute, algo, features, model, list(label_binerizer.classes_),
                                           test_twitter_ids, y_test_inv, y_pred_inv, y_pred_proba)
