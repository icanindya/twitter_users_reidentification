from collections import defaultdict

import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize.casual import TweetTokenizer
from nltk.util import ngrams

import helper

tweet_tokenizer = TweetTokenizer(preserve_case=True, reduce_len=False, strip_handles=False)
porter_stemmer = PorterStemmer()
stopwords = list(stopwords.words('english'))

unwanted = stopwords

onegram_freq = defaultdict(int)
twogram_freq = defaultdict(int)

MAX = 10000

count = 0


def is_unwanted(token):
    return token in unwanted or helper.is_link(token)


def text_processor(text):
    global count
    count += 1
    if count % 1000 == 0:
        print('data read: {}'.format(count))
    text = text.lower()
    text = text.replace('\t', ' ')
    text = text.replace('\r\n', ' ')
    text = text.replace('\r', ' ')
    text = text.replace('\n', ' ')
    tokens = tweet_tokenizer.tokenize(text)
    stems = [porter_stemmer.stem(token) for token in tokens]
    stems = [stem for stem in stems if not is_unwanted(stem)]
    onegram_list = [' '.join(ngram) for ngram in ngrams(stems, 1)]
    twogram_list = [' '.join(ngram) for ngram in ngrams(stems, 2)]

    return (onegram_list, twogram_list)


YEARLY_TWEETS_COMBINED_PATH = r'D:\Data\Linkage\FL\FL18\tweets\maif_yearly_tweets_combined.csv'
ALL_TWEETS_COMBINED_PATH = r'D:\Data\Linkage\FL\FL18\tweets\maif_all_tweets_combined.csv'
input_col_names = ['twitter_id', 'doc', 'dob_or_age', 'sex', 'race_code', 'zip_code', 'city', 'party']
maif_input_col_names = ['twitter_id', 'doc', 'dob_or_age']
input_ds_path = ALL_TWEETS_COMBINED_PATH

data = pd.read_csv(input_ds_path, encoding='utf-8', names=maif_input_col_names)
data_size = data.shape[0]

df = data.loc[:, ['doc', 'dob_or_age']]

with open(r'D:\Data\Linkage\FL\FL18\tweets\maif_1grams_label.txt', 'w', encoding='utf-8') as wf1:
    with open(r'D:\Data\Linkage\FL\FL18\tweets\maif_2grams_label.txt', 'w', encoding='utf-8') as wf2:

        for i, row in df.iterrows():

            ngram_list = text_processor(row['doc'])
            onegram_list = ngram_list[0]
            twogram_list = ngram_list[1]

            for token in onegram_list:
                onegram_freq[token] += 1
            for token in twogram_list:
                twogram_freq[token] += 1

            age = str(row['dob_or_age'])

            wf1.write('\t'.join(onegram_list) + '\t{}\n'.format(age))
            wf2.write('\t'.join(twogram_list) + '\t{}\n'.format(age))

print('num of one grams: {}'.format(len(onegram_freq)))
print('num of two grams: {}'.format(len(twogram_freq)))

top_onegrams = sorted(onegram_freq.keys(), key=lambda k: onegram_freq[k], reverse=True)[:MAX]
top_twograms = sorted(twogram_freq.keys(), key=lambda k: twogram_freq[k], reverse=True)[:MAX]

with open(r'D:\Data\Linkage\FL\FL18\tweets\maif_top_onegrams.txt', 'w', encoding='utf-8') as wf:
    wf.write('\n'.join(top_onegrams))

with open(r'D:\Data\Linkage\FL\FL18\tweets\maif_top_twograms.txt', 'w', encoding='utf-8') as wf:
    wf.write('\n'.join(top_twograms))
