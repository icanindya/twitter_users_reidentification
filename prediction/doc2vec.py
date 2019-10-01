import csv
import sys
import time

import gensim

maxInt = sys.maxsize
csv.field_size_limit(sys.maxsize)

while True:
    # decrease the maxInt value by factor 10 
    # as long as the OverflowError occurs.

    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt / 10)

ALL_TWEETS_TOKENS_PATH = r'D:\Data\Linkage\FL\FL18\tweets\all_tweets_tokens.csv'
ALL_TWEETS_MODEL_PATH = r'D:\Data\Linkage\FL\FL18\tweets\all_tweets_d2v_{}.model'
ALL_TWEETS_D2V_FEATURES_PATH = r'D:\Data\Linkage\FL\FL18\tweets\all_tweets_d2v_{}_features.csv'
YEARLY_TWEETS_TOKENS_PATH = r'D:\Data\Linkage\FL\FL18\tweets\yearly_tweets_tokens.csv'
YEARLY_TWEETS_MODEL_PATH = r'D:\Data\Linkage\FL\FL18\tweets\yearly_tweets_d2v_{}.model'
YEARLY_TWEETS_D2V_FEATURES_PATH = r'D:\Data\Linkage\FL\FL18\tweets\yearly_tweets_d2v_{}_features.csv'


def vectorize_docs(tokens_path, model_path, features_path, vec_size):
    start = time.time()

    class Corpus(object):
        def __iter__(self):
            with open(tokens_path, 'r', encoding='utf-8') as rf:
                csv_reader = csv.reader(rf, delimiter=',')
                for i, row in enumerate(csv_reader):
                    # assume there's one document per line, tokens separated by whitespace
                    yield gensim.models.doc2vec.TaggedDocument(words=row[1].split(), tags=[i])

    model = gensim.models.doc2vec.Doc2Vec(documents=Corpus(), vector_size=vec_size, window=4, min_count=10, workers=4)
    model.save(model_path)

    read_count = 0

    with open(features_path, 'w', newline='', encoding='utf-8') as wf:
        csv_writer = csv.writer(wf, delimiter=',')
        with open(tokens_path, 'r', encoding='utf-8') as rf:
            csv_reader = csv.reader(rf, delimiter=',')
            for i, row in enumerate(csv_reader):
                read_count += 1
                tokens = row[1].split()
                d2v_vector = list(map(str, model.infer_vector(tokens)))
                write_row_items = [row[0]] + d2v_vector + row[2:]
                csv_writer.writerow(write_row_items)

    end = time.time()

    print('csv lines: {}, time: {}'.format(read_count, (end - start)))


if __name__ == '__main__':

    option = int(sys.argv[1])
    vec_size = int(sys.argv[2])

    if option == 0:
        tokens_path = ALL_TWEETS_TOKENS_PATH
        model_path = ALL_TWEETS_MODEL_PATH.format(vec_size)
        features_path = ALL_TWEETS_D2V_FEATURES_PATH.format(vec_size)
    elif option == 1:
        tokens_path = YEARLY_TWEETS_TOKENS_PATH
        model_path = YEARLY_TWEETS_MODEL_PATH.format(vec_size)
        features_path = YEARLY_TWEETS_D2V_FEATURES_PATH.format(vec_size)

    vectorize_docs(tokens_path, model_path, features_path, vec_size)
