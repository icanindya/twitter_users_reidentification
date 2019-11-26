import numpy as np
import time
import csv
import sys
import os
import helper

helper.set_csv_field_size_limit()

ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv'
YEARLY_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\yearly_tweets.csv'

GLOVE_PRETRAINED_MODEL_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\glove.twitter.27B.100d.txt'
GLOVE_EMBEDDING_SIZE = 100


def vectorize_docs(tokens_path, model_path, features_path):

    print('loading prebuilt model')
    start = time.time()
    glove_embedding = {}
    with open(model_path, 'r', encoding='utf-8') as rf:
        for line in rf:
            tokens = line.split()
            word = tokens[0]
            embedding = np.array([float(val) for val in tokens[1:]])
            glove_embedding[word] = embedding
    end = time.time()
    print('model with size {} loaded in {} sec(s)'.format(len(glove_embedding),  (end - start)))

    print('started records generation')
    strat = time.time()

    with open(features_path, 'w', newline='', encoding='utf-8') as wf:
        csv_writer = csv.writer(wf, delimiter=',')
        csv_writer.writerow(['glove-{}'.format(i) for i in range(GLOVE_EMBEDDING_SIZE)])

        with open(tokens_path, 'r', encoding='utf-8') as rf:
            csv_reader = csv.DictReader(rf, delimiter=',')

            for i, row in enumerate(csv_reader):
                if i % 100 == 0:
                    print('write csv row', i)
                tokens = [x.lower() for x in row['tokens_joined'].split() if not helper.stop_or_mention(x)]
                embedding_matrix = np.zeros((len(tokens), GLOVE_EMBEDDING_SIZE), dtype='float32')
                for j, token in enumerate(tokens):
                    if token in glove_embedding:
                        embedding_vector = glove_embedding[token]
                        embedding_matrix[j] = embedding_vector
                    # words not found are all-zeros by default

                glove_vector = [str(x) for x in embedding_matrix.mean(axis=0)]
                csv_writer.writerow(glove_vector)

    end = time.time()
    print('generated {} records in {} sec(c)'.format(i + 1, (end - start)))


if __name__ == '__main__':

    option = sys.argv[1]

    if option == '1':
        dataset_path = ALL_TWEETS_PATH

    elif option == '2':
        dataset_path = YEARLY_TWEETS_PATH

    model_path = GLOVE_PRETRAINED_MODEL_PATH

    file_name, file_ext = os.path.splitext(dataset_path)
    tokens_path = file_name + '_tokens.csv'

    features_path = file_name + '_glove_{}_features.csv'.format(GLOVE_EMBEDDING_SIZE)
    vectorize_docs(tokens_path, model_path, features_path)
