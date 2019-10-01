import numpy as np
import pandas as pd
from keras.layers import Dense
from keras.models import Sequential
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer
from sklearn.preprocessing import StandardScaler
from sklearn.utils import shuffle

import helper

dnn = True

ALL_TWEETS_D2V_FEATURES_PATH = r'D:\Data\Linkage\FL\FL18\tweets\all_tweets_d2v_{}_features.csv'
YEARLY_TWEETS_D2V_FEATURES_PATH = r'D:\Data\Linkage\FL\FL18\tweets\yearly_tweets_d2v_{}_features.csv'
RESULT_PATH = r'D:\Data\Linkage\FL\FL18\tweets\dnn_d2v_{}_result.txt'

if __name__ == '__main__':

    for attribute in ['party']:

        for vec_size in [100, 200, 300]:

            if attribute == 'age':
                label_index = -6
                dataset_path = YEARLY_TWEETS_D2V_FEATURES_PATH.format(vec_size)
            elif attribute == 'sex':
                label_index = -5
                dataset_path = ALL_TWEETS_D2V_FEATURES_PATH.format(vec_size)
            elif attribute == 'race':
                label_index = -4
                dataset_path = ALL_TWEETS_D2V_FEATURES_PATH.format(vec_size)
            elif attribute == 'party':
                label_index = -1
                dataset_path = ALL_TWEETS_D2V_FEATURES_PATH.format(vec_size)

            col_names = ['twitter_id'] + \
                        ['feature_{}'.format(i) for i in range(vec_size)] + \
                        ['dob_or_age', 'sex', 'race_code', 'zip_code', 'city', 'party']

            df = pd.read_csv(dataset_path, names=col_names)
            df = df.dropna(subset=['dob_or_age', 'sex', 'race_code', 'zip_code', 'city', 'party'])
            df = shuffle(df)

            X = df.iloc[:, 1:1 + vec_size].values
            y = df.iloc[:, label_index].values

            if attribute == 'age':
                y = np.array(list(map(lambda age: helper.get_maif_age_label(age), y)))
            elif attribute == 'race':
                y = np.array(list(map(lambda code: helper.get_race_label(code), y)))

            if dnn:

                labels = np.unique(y)

                label_binerizer = LabelBinarizer()
                y = label_binerizer.fit_transform(y)

                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

                scaler = StandardScaler()
                X_train = scaler.fit_transform(X_train)
                X_test = scaler.transform(X_test)

                for num_hl in range(1, 31):

                    num_inputs = vec_size
                    num_outputs = len(labels)
                    var_hl_size = int((num_inputs * (2 / 3) + num_outputs) // num_hl)
                    fixed_hl_size = int((num_inputs + num_outputs) // 2)

                    for num_nodes_per_hl in [fixed_hl_size]:

                        model = Sequential()
                        model.add(Dense(num_nodes_per_hl, activation='relu', input_dim=num_inputs))
                        for i in range(num_hl - 1):
                            model.add(Dense(num_nodes_per_hl, activation='relu'))
                        model.add(Dense(num_outputs, activation='softmax'))

                        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
                        model.fit(X_train, y_train, epochs=50, batch_size=100)

                        scores = model.evaluate(X_test, y_test)

                        y_pred = model.predict(X_test)
                        y_pred_orig = label_binerizer.inverse_transform(y_pred)
                        y_test_orig = label_binerizer.inverse_transform(y_test)

                        cm = confusion_matrix(y_test_orig, y_pred_orig, labels=labels)
                        cm_df = pd.DataFrame(cm, index=labels, columns=labels)

                        with open(RESULT_PATH.format(attribute), 'a') as wf:
                            wf.write('attribute: {}'.format(attribute) + '\n')
                            wf.write('dataset size: {}, test: 0.3\n'.format(len(X)))
                            wf.write('doc2vec size: {}'.format(vec_size) + '\n')
                            wf.write('hidden layers: {}, nodes per layer: {}'.format(num_hl, num_nodes_per_hl) + '\n')
                            wf.write('{}: {:.2f}'.format(model.metrics_names[1], scores[1] * 100) + '\n')
                            wf.write('confusion matrix:' + '\n')
                            wf.write('\n')
                            wf.write(str(cm_df) + '\n')
                            wf.write('\n\n')
                            wf.flush()

            else:
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

                clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=0)

                clf.fit(X_train, y_train)

                y_pred = clf.predict(X_test)

                acc = accuracy_score(y_test, y_pred)

                labels = list(set(y))

                cm = confusion_matrix(y_test, y_pred, labels=labels)
                cm_df = pd.DataFrame(cm, index=labels, columns=labels)

                RESULT_PATH = r'D:\Data\Linkage\FL\FL18\tweets\rf_d2v_{}_result.txt'

                with open(RESULT_PATH.format(attribute), 'a') as wf:
                    wf.write('attribute: {}\n'.format(attribute))
                    wf.write('dataset size: {}, test: 0.2\n'.format(len(X)))
                    wf.write('doc2vec size: {}\n'.format(vec_size))
                    wf.write('acc: {}\n'.format(acc))
                    wf.write(str(cm_df) + '\n\n')
