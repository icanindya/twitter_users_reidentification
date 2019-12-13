import csv
import sys
import time
import os
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize.casual import TweetTokenizer
from nltk.util import ngrams
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import helper


helper.set_csv_field_size_limit()

TOP_SIZE = 10000

ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv'
YEARLY_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\yearly_tweets.csv'

TOP_1GRAMS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\top_1grams.txt'
TOP_2GRAMS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\top_2grams.txt'

porter_stemmer = PorterStemmer()


def process_text(text):

    tokens_lower = [x.lower() for x in text.split() if not helper.stop_mention_url_or_symbol(x)]
    stems = [porter_stemmer.stem(token) for token in tokens_lower]
    onegrams = [' '.join(ngram) for ngram in ngrams(stems, 1)]
    twograms = [' '.join(ngram) for ngram in ngrams(stems, 2)]
    return onegrams + twograms


def get_top_grams(root_tokens_path):

    if not os.path.exists(TOP_1GRAMS_PATH) or not os.path.exists(TOP_2GRAMS_PATH):

        onegram_freq = defaultdict(int)
        twogram_freq = defaultdict(int)

        with open(root_tokens_path, 'r', encoding='utf-8') as rf:
            csv_reader = csv.DictReader(rf, delimiter=',')
            for i, row in enumerate(csv_reader):
                if i % 100 == 0:
                    print('read csv row for model', i)
                tokens_lower = [x.lower() for x in row['tokens_joined'].split() if not helper.stop_mention_url_or_symbol(x)]
                stems = [porter_stemmer.stem(token) for token in tokens_lower]
                onegrams = [' '.join(ngram) for ngram in ngrams(stems, 1)]
                twograms = [' '.join(ngram) for ngram in ngrams(stems, 2)]

                for onegram in onegrams:
                    onegram_freq[onegram] += 1

                for twogram in twograms:
                    twogram_freq[twogram] += 1

        onegrams_sorted = sorted(onegram_freq.keys(), key=lambda k: onegram_freq[k], reverse=True)
        twograms_sorted = sorted(twogram_freq.keys(), key=lambda k: twogram_freq[k], reverse=True)

        with open(TOP_1GRAMS_PATH, 'w', encoding='utf-8') as wf:
            for onegram in onegrams_sorted:
                wf.write('{}\n'.format(onegram))

        with open(TOP_2GRAMS_PATH, 'w', encoding='utf-8') as wf:
            for twogram in twograms_sorted:
                wf.write('{}\n'.format(twogram))

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


def vectorize_docs(dataset_tokens_path, top_grams, model_path):
    if not os.path.exists(model_path):
        class Corpus(object):
            def __iter__(self):
                with open(dataset_tokens_path, 'r', encoding='utf-8') as rf:
                    csv_reader = csv.DictReader(rf, delimiter=',')
                    for i, row in enumerate(csv_reader):
                        if i % 100 == 0:
                            print('read csv row', i)
                        # assume there's one document per line, tokens separated by whitespace
                        yield row['tokens_joined']

        vectorizer = TfidfVectorizer(analyzer=process_text, vocabulary=top_grams)
        tfidf = vectorizer.fit_transform(Corpus().__iter__())
        joblib.dump(tfidf, model_path)


if __name__ == '__main__':

    option = '2'

    if len(sys.argv) > 1:
        option = sys.argv[1]

    if option == '1':
        dataset_path = ALL_TWEETS_PATH

    elif option == '2':
        dataset_path = YEARLY_TWEETS_PATH

    file_name, file_ext = os.path.splitext(ALL_TWEETS_PATH)
    root_tokens_path = file_name + '_tokens.csv'

    file_name, file_ext = os.path.splitext(dataset_path)
    dataset_tokens_path = file_name + '_tokens.csv'

    model_path = file_name + '_tfidf_{}.model'.format(TOP_SIZE * 2)
    top_grams = get_top_grams(root_tokens_path)

    print(len(top_grams))

    vectorize_docs(dataset_tokens_path, top_grams, model_path)

    tfidf = joblib.load(model_path)

    print(tfidf.shape)