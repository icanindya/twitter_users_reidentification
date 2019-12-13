import csv
import sys
import time
import os
import gensim
import helper

helper.set_csv_field_size_limit()

FASTTEXT_EMBEDDING_SIZE = 100

ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv'
YEARLY_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\yearly_tweets.csv'


def get_model(model_tokens_path, model_path):

    if os.path.exists(model_path):
        print('loading prebuilt model')
        model = gensim.models.fasttext.FastText.load(model_path)
        print('loaded prebuilt model')
    else:
        class Corpus(object):
            def __iter__(self):
                with open(model_tokens_path, 'r', encoding='utf-8') as rf:
                    csv_reader = csv.DictReader(rf, delimiter=',')
                    for i, row in enumerate(csv_reader):
                        if i % 100 == 0:
                            print('read csv row', i)
                        # assume there's one document per line, tokens separated by whitespace
                        tokens = [x.lower() for x in row['tokens_joined'].split() if not helper.stop_or_mention(x)]
                        yield tokens

        print('started model generation')
        start = time.time()

        model = gensim.models.fasttext.FastText(sentences=Corpus(), size=FASTTEXT_EMBEDDING_SIZE, iter=20, window=4, min_count=100, workers=4)
        model.save(model_path)

        end = time.time()
        print('model generated in {} sec(s)', (end - start))

    return model


def vectorize_docs(model, dataset_tokens_path, features_path):

    print('started records generation')
    start = time.time()

    with open(features_path, 'w', newline='', encoding='utf-8') as wf:
        csv_writer = csv.writer(wf, delimiter=',')
        csv_writer.writerow(['ftext-{}'.format(i) for i in range(FASTTEXT_EMBEDDING_SIZE)])

        with open(dataset_tokens_path, 'r', encoding='utf-8') as rf:
            csv_reader = csv.DictReader(rf, delimiter=',')

            for i, row in enumerate(csv_reader):
                if i % 100 == 0:
                    print('write csv row', i)
                tokens = [x.lower() for x in row['tokens_joined'].split() if not helper.stop_or_mention(x)]
                ftext_vector = [str(x) for x in model.infer_vector(tokens)]
                csv_writer.writerow(ftext_vector)

    end = time.time()
    print('generated {} records in {} sec(c)'.format(i + 1, (end - start)))


if __name__ == '__main__':

    option = sys.argv[1]

    if option == '1':
        dataset_path = ALL_TWEETS_PATH

    elif option == '2':
        dataset_path = YEARLY_TWEETS_PATH

    file_name, file_ext = os.path.splitext(ALL_TWEETS_PATH)
    model_tokens_path = file_name + '_tokens.csv'
    model_path = file_name + '_ftext_{}.model'.format(FASTTEXT_EMBEDDING_SIZE)

    file_name, file_ext = os.path.splitext(dataset_path)
    dataset_tokens_path = file_name + '_tokens.csv'

    features_path = file_name + '_ftext_{}_features.csv'.format(FASTTEXT_EMBEDDING_SIZE)

    model = get_model(model_tokens_path, model_path)

    vectorize_docs(model, dataset_tokens_path, model_path, features_path)
