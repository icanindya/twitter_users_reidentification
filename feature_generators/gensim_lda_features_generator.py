import csv
import sys
import time
import os
import gensim
import helper
from gensim.models.ldamodel import *
from nltk.corpus import stopwords

stopwords = set(stopwords.words('english'))

LDA_FEATURES_SIZE = 60

ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv'
YEARLY_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\yearly_tweets.csv'
SINGLE_TWEET_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\single_tweet.csv'
SINGLE_TWEET_TOKENS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\single_tweet_tokens.csv'
DICTIONARY_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\tweets_lda.dict'


def get_model(model_tokens_path, model_path):

    if os.path.exists(model_path):
        print('loading prebuilt model')
        model = gensim.models.ldamodel.LdaModel.load(model_path)
        print('loaded prebuilt model')
    else:

        print('started dictionary generation')
        start = time.time()

        all_tokens = set()

        with open(model_tokens_path, 'r', encoding='utf-8') as rf:
            csv_reader = csv.DictReader(rf, delimiter=',')
            for i, row in enumerate(csv_reader):
                if i % 1000 == 0:
                    print('read csv row for dictionary', i)
                # assume there's one document per line, tokens separated by whitespace
                tokens = [x.lower() for x in row['tokens_joined'].split() if not helper.stop_or_mention(x)]
                all_tokens.update(tokens)
        dictionary = gensim.corpora.Dictionary([list(all_tokens)])

        end = time.time()
        print('dictionary generated in {} sec(s)', (end - start))

        print('started model generation')
        start = time.time()

        class Corpus(object):

            def __iter__(self):
                with open(model_tokens_path, 'r', encoding='utf-8') as rf:
                    csv_reader = csv.DictReader(rf, delimiter=',')
                    for i, row in enumerate(csv_reader):
                        if i % 1000 == 0:
                            print('read csv row for model', i)
                        # assume there's one document per line, tokens separated by whitespace
                        tokens = [x.lower() for x in row['tokens_joined'].split()]
                        yield dictionary.doc2bow(tokens)

        print('started model generation')
        start = time.time()

        model = gensim.models.ldamodel.LdaModel(corpus=Corpus(), id2word=dictionary, num_topics=LDA_FEATURES_SIZE, alpha='auto', passes=1)
        model.save(model_path)

        end = time.time()
        print('model generated in {} sec(s)', (end - start))

    return model


def vectorize_docs(model, dataset_tokens_path, features_path):

    print('started records generation')
    start = time.time()

    with open(features_path, 'w', newline='', encoding='utf-8') as wf:
        csv_writer = csv.writer(wf, delimiter=',')
        csv_writer.writerow(['lda-{}'.format(i) for i in range(LDA_FEATURES_SIZE)])

        with open(dataset_tokens_path, 'r', encoding='utf-8') as rf:
            csv_reader = csv.DictReader(rf, delimiter=',')

            for i, row in enumerate(csv_reader):
                if i % 100 == 0:
                    print('write csv row', i)
                tokens = [x.lower() for x in row['tokens_joined'].split()]
                bow = model.id2word.doc2bow(tokens)
                # print(bow)

                index_probs = model.get_document_topics(bow)
                lda_vector = [0.] * LDA_FEATURES_SIZE

                for i, p in index_probs:
                    lda_vector[i] = p

                csv_writer.writerow(lda_vector)

    end = time.time()
    print('generated {} records in {} sec(c)'.format(i + 1, (end - start)))


if __name__ == '__main__':

    option = '1'
    mode = 'doc'

    if len(sys.argv) > 2:
        option = sys.argv[1]
        mode = sys.argv[2]

    if option == '1':
        dataset_path = ALL_TWEETS_PATH

    elif option == '2':
        dataset_path = YEARLY_TWEETS_PATH

    if mode == 'doc':
        file_name, file_ext = os.path.splitext(ALL_TWEETS_PATH)
        model_tokens_path = file_name + '_tokens.csv'
        model_path = file_name + '_lda_{}.model'.format(LDA_FEATURES_SIZE)
    elif mode == 'tweet':
        file_name, file_ext = os.path.splitext(SINGLE_TWEET_PATH)
        model_tokens_path = file_name + '_tokens.csv'
        model_path = file_name + '_lda_{}.model'.format(LDA_FEATURES_SIZE)

    file_name, file_ext = os.path.splitext(dataset_path)
    dataset_tokens_path = file_name + '_tokens.csv'

    features_path = file_name + '_lda_{}_{}_features.csv'.format(LDA_FEATURES_SIZE, mode)

    model = get_model(model_tokens_path, model_path)

    # for i, topic in model.show_topics(num_topics=LDA_FEATURES_SIZE, formatted=False, num_words=20):
    #     print('Topic {}: {}'.format(i, ', '.join([w[0] for w in topic])))

    vectorize_docs(model, dataset_tokens_path, features_path)
