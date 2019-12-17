import pandas as pd
import numpy as np
import sys
import os
import helper
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

ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv'
YEARLY_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\yearly_tweets.csv'
NUM_TWEETS = 50
SELECTED_TWITTER_IDS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\twitter_ids_{}_tweets.csv'.format(NUM_TWEETS)
PREDICTION_PATH = r'D:\Data\Linkage\FL\FL18\results\predictions\{}_{}_{}.csv'

TOP_1GRAMS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\top_1grams.txt'
TOP_2GRAMS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\top_2grams.txt'

# NGRAMS_TRAIN_FEATURES_PATH =
# NGRAMS_TEST_FEATURES_PATH =

porter_stemmer = PorterStemmer()


def get_top_grams(TOP_SIZE):

    top_onegrams = set()
    top_twograms = set()

    with open(TOP_1GRAMS_PATH, 'r', encoding='utf-8') as rf:
        for i, line in enumerate(rf):
            top_onegrams.add(line.strip())
            if i == TOP_SIZE - 1:
                break

    with open(TOP_2GRAMS_PATH, 'r', encoding='utf-8') as rf:
        for i, line in enumerate(rf):
            top_twograms.add(line.strip())
            if i == TOP_SIZE - 1:
                break

    return list(top_onegrams.union(top_twograms))


def process_text(row):

    text = row[0]
    tokens_lower = [x.lower() for x in text.split() if not helper.stop_mention_url_or_symbol(x)]
    stems = [porter_stemmer.stem(token) for token in tokens_lower]
    onegrams = [' '.join(ngram) for ngram in ngrams(stems, 1)]
    twograms = [' '.join(ngram) for ngram in ngrams(stems, 2)]

    return onegrams + twograms


def neural_net(X_train, y_train, X_test, y_test, output_dim, hidden_len):

    input_dim = X_train.shape[1]
    hidden_dim = (input_dim + output_dim) // 2

    model = Sequential()
    model.add(Dense(hidden_dim, activation='relu', input_dim=input_dim))
    for i in range(hidden_len):
        model.add(Dense(hidden_dim, activation='relu'))
    model.add(Dense(output_dim, activation='softmax'))

    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=50, batch_size=128)

    scores = model.evaluate(X_test, y_test)
    accuracy = scores[1] * 100
    y_pred = model.predict(X_test)

    return accuracy, y_pred


def random_forest(X_train, y_train, X_test, y_test):

    model = RandomForestClassifier(n_estimators=500, max_depth=None, random_state=helper.random_seed)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred) * 100

    return accuracy, y_pred


def save_predictions(attribute, algo, features, predictions):

    with open(PREDICTION_PATH.format(attribute, algo, '-'.join(features)), 'w', newline='', encoding='utf-8') as wf:
        csv_writer = csv.writer(wf, delimiter=',')
        csv_writer.writerow(['predictions'])

        for prediction in predictions:
            csv_writer.writerow([prediction])


if len(sys.argv) > 1:
    attribute_list = [sys.argv[1]]
    algo_list = [sys.argv[2]]
    features = []
    for i in range(3, len(sys.argv)):
        features.append(sys.argv[i])
    features_list = [features]

else:
    attribute_list = ['sex', 'race', 'party']
    algo_list = ['random-forest']
    features_list = [['ngrams']]

ids_df = pd.read_csv(SELECTED_TWITTER_IDS_PATH, header=0)
test_ids_df = ids_df.sample(frac=helper.test_percentage, random_state=helper.random_seed)
test_ids = test_ids_df['twitter_ids'].tolist()
train_ids_df = ids_df.drop(test_ids_df.index)
train_ids = train_ids_df['twitter_ids'].tolist()

with open(r'D:\Data\Linkage\FL\FL18\results\results.txt', 'a', encoding='utf-8') as wf:

    for features in features_list:
        for algo in algo_list:
            for attribute in attribute_list:

                print('attribute: {} | features: {} | algorithm: {}'.format(attribute, ','.join(features), algo))

                df_list = []

                if attribute == 'age':
                    dataset_path = YEARLY_TWEETS_PATH
                    df = pd.read_csv(dataset_path, header=0, usecols=['twitter_id', attribute])
                    df['age'] = df['age'].apply(helper.get_maif_age_label)
                    df_list.append(df)
                else:
                    dataset_path = ALL_TWEETS_PATH
                    df = pd.read_csv(dataset_path, header=0, usecols=['twitter_id', attribute])
                    if attribute == 'race':
                        df['race'] = df['race'].apply(helper.get_text_race_code)
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
                    df_list.append(pd.read_csv(features_path, header=0))

                if 'textual' in features:
                    features_path = file_name + '_textual_features.csv'
                    df_list.append(pd.read_csv(features_path, header=0))

                if 'lda' in features:
                    features_path = file_name + '_lda_60_doc_features.csv'
                    df_list.append(pd.read_csv(features_path, header=0))

                if 'ngrams' in features:
                    # df_list.append(pd.read_csv(dataset_path, header=0, usecols=['text']))
                    model_path = file_name + '_tfidf_20000.model'
                    tfidf = joblib.load(model_path)
                    df_list.append(pd.DataFrame(tfidf.todense()))

                df = pd.concat(df_list, axis=1)

                train_df = df.loc[df['twitter_id'].isin(train_ids)]
                test_df = df.loc[df['twitter_id'].isin(test_ids)]

                X_train = train_df.drop(['twitter_id', attribute], axis=1).values
                y_train = np.array(train_df[attribute])
                X_test = test_df.drop(['twitter_id', attribute], axis=1).values
                y_test = np.array(test_df[attribute])

                # if 'ngrams' in features:
                #     top_grams = get_top_grams(10000)
                #     vectorizer = TfidfVectorizer(analyzer=process_text, vocabulary=top_grams)
                #     X_train = vectorizer.fit_transform(X_train)
                #     X_test = vectorizer.transform(X_test)
                #     joblib.dump(X_train, file_name + '_ngram_train_{}_features.bin'.format(len(top_grams)))
                #     joblib.dump(X_test, file_name + '_ngram_test_{}_features.bin'.format(len(top_grams)))

                scaler = StandardScaler()
                X_train = scaler.fit_transform(X_train)
                X_test = scaler.transform(X_test)

                y = np.concatenate((y_train, y_test))
                label_binerizer = LabelBinarizer().fit(y)
                y_train = label_binerizer.transform(y_train)
                y_test = label_binerizer.transform(y_test)
                y_test_inv = label_binerizer.inverse_transform(y_test)

                if algo == 'neural-network':
                    accuracy, y_pred = neural_net(X_train, y_train, X_test, y_test, output_dim=len(label_binerizer.classes_), hidden_len=1)

                elif algo == 'random-forest':
                    accuracy, y_pred = random_forest(X_train, y_train, X_test, y_test)

                y_pred_inv = label_binerizer.inverse_transform(y_pred)

                cm = confusion_matrix(y_test_inv, y_pred_inv, labels=label_binerizer.classes_)
                cm_df = pd.DataFrame(cm, index=label_binerizer.classes_, columns=label_binerizer.classes_)
                cm_df.sort_index(axis=1, inplace=True)

                # print('attribute: {} | features: {} | algorithm: {}\n'.format(attribute, ','.join(features), algo))
                print('accuracy: {:.2f}\n'.format(accuracy))
                print('confusion matrix:\n')
                print('{}\n\n'.format(str(cm_df)))

                wf.write('attribute: {} | features: {} | algorithm: {}\n'.format(attribute, ','.join(features), algo))
                wf.write('accuracy: {:.2f}\n'.format(accuracy))
                wf.write('confusion matrix:\n')
                wf.write('{}\n\n'.format(str(cm_df)))
                wf.flush()

                # save_predictions(attribute, algo, features, y_pred_inv)



# 82.63 75.54, 52.13
#ngram: 68, 22











