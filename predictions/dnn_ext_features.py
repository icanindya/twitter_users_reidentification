import numpy as np
import pandas as pd
from keras.layers import Dense
from keras.models import Sequential
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer
from sklearn.preprocessing import StandardScaler
from sklearn.utils import shuffle

import helper

YEARLY_TWEETS_EXT_FEATURES_PATH = r'D:\Data\Linkage\FL\FL18\tweets\yearly_tweets_ext_features.csv'
RESULT_PATH = r'D:\Data\Linkage\FL\FL18\tweets\dnn_ext_age_result.txt'

if __name__ == '__main__':
    vec_size = 263
    attribute = 'age'
    if attribute == 'age':
        label_index = -6
        dataset_path = YEARLY_TWEETS_EXT_FEATURES_PATH

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

    labels = np.unique(y)

    label_binerizer = LabelBinarizer()
    y = label_binerizer.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    for num_hl in [1, 2, 3]:

        num_inputs = vec_size
        num_outputs = len(labels)
        var_hl_size = int((num_inputs * (2 / 3) + num_outputs) // num_hl)
        fixed_hl_size = int((num_inputs + num_outputs) // 2)

        for num_nodes_per_hl in [var_hl_size, fixed_hl_size]:

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
                wf.write('doc2vec size: {}'.format(vec_size) + '\n')
                wf.write('hidden layers: {}, nodes per layer: {}'.format(num_hl, num_nodes_per_hl) + '\n')
                wf.write('{}: {:.2f}'.format(model.metrics_names[1], scores[1] * 100) + '\n')
                wf.write('confusion matrix:' + '\n')
                wf.write('\n')
                wf.write(str(cm_df) + '\n')
                wf.write('\n\n')
                wf.flush()
