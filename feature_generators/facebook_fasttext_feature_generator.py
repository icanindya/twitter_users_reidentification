import fasttext
import csv
import helper
import os
import sys
import time
import unicodedata

ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv'
YEARLY_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\yearly_tweets.csv'
TRAINER_TWEET_TOKENS_PATH = r"D:\Data\Linkage\FL\FL18\ml_datasets\trainer_tweet_tokens.csv"

FASTEXT_EMBEDDING_SIZE = 100
MODEL_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\fb_ftext_twitter_{}.model'.format(FASTEXT_EMBEDDING_SIZE)


def preprocess(text):

    text = ''.join(c for c in text if unicodedata.category(c).startswith(('C', )) is False)
    text = ''.join(' ' if unicodedata.category(c).startswith(('Zl', 'Zp')) else c for c in text)
    tokenizer = helper.CustomTweetTokenizer(preserve_case=False, reduce_len=False, strip_handles=True, convert_urls=True, remove_stopwords=True)
    tokens = tokenizer.tokenize(text)
    return ' '.join(tokens)


def get_model(fb_ftext_input_path=TRAINER_TWEET_TOKENS_PATH, model_path=MODEL_PATH):

    if os.path.exists(model_path):
        print('loading prebuilt model')
        model = fasttext.load_model(model_path)
        print('loaded prebuilt model')
    else:
        print('started model generation')
        start = time.time()

        model = fasttext.train_unsupervised(input=fb_ftext_input_path, model='cbow', dim=100, epoch=20, ws=4, minCount=100, thread=4)
        model.save_model(model_path)

        end = time.time()
        print('model generated in {} sec(s)'.format(end - start))

    return model


def vectorize_docs(model, dataset_tokens_path, features_path):

    if not os.path.exists(features_path):

        print('started records generation')
        start = time.time()

        with open(features_path, 'w', newline='', encoding='utf-8') as wf:
            csv_writer = csv.writer(wf, delimiter=',')
            csv_writer.writerow(['ftext-{}'.format(i) for i in range(FASTEXT_EMBEDDING_SIZE)])

            with open(dataset_tokens_path, 'r', encoding='utf-8') as rf:
                csv_reader = csv.DictReader(rf, delimiter=',')

                for i, row in enumerate(csv_reader):
                    if i % 100 == 0:
                        print('write csv row', i)

                    # tokens = [x.lower() for x in row['tokens_joined'].split() if not helper.mention(x)]

                    ftext_vector = model.get_sentence_vector(preprocess(row['tokens_joined']))
                    csv_writer.writerow(ftext_vector)

        end = time.time()
        print('generated {} records in {} sec(c)'.format(i + 1, (end - start)))


if __name__ == '__main__':

    option = '1'

    if len(sys.argv) > 1:
        option = sys.argv[1]

    if option == '1':
        dataset_path = ALL_TWEETS_PATH

    elif option == '2':
        dataset_path = YEARLY_TWEETS_PATH

    file_name, file_ext = os.path.splitext(ALL_TWEETS_PATH)
    fb_ftext_input_path = file_name + '_fb_ftext_input.txt'
    model_path = file_name + '_fb_ftext_{}.model'.format(FASTEXT_EMBEDDING_SIZE)

    file_name, file_ext = os.path.splitext(dataset_path)
    dataset_tokens_path = file_name + '_tokens.csv'

    features_path = file_name + '_fb_ftext_{}_features.csv'.format(FASTEXT_EMBEDDING_SIZE)

    model = get_model(fb_ftext_input_path=fb_ftext_input_path, model_path=model_path)

    vectorize_docs(model, dataset_tokens_path, features_path)