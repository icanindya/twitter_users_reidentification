import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize.casual import TweetTokenizer
from nltk.util import ngrams

import helper

tweet_tokenizer = TweetTokenizer(preserve_case=True, reduce_len=False, strip_handles=False)
porter_stemmer = PorterStemmer()
stopwords = list(stopwords.words('english'))
unwanted = stopwords + ['\t', '\n']

YEARLY_TWEETS_COMBINED_PATH = r'D:\Data\Linkage\FL\FL18\tweets\yearly_tweets_combined.csv'
ALL_TWEETS_COMBINED_PATH = r'D:\Data\Linkage\FL\FL18\tweets\all_tweets_combined.csv'
input_col_names = ['twitter_id', 'doc', 'dob_or_age', 'sex', 'race_code', 'zip_code', 'city', 'party']
input_ds_path = YEARLY_TWEETS_COMBINED_PATH

df = pd.read_csv(input_ds_path, encoding='utf-8', names=input_col_names, nrows=357)
df = df.loc[:, ['doc', 'dob_or_age']]


def is_unwanted(token):
    return token in unwanted or helper.is_link(token)


def process_text(text):
    tokens = tweet_tokenizer.tokenize(text)
    stems = [porter_stemmer.stem(token) for token in tokens]
    stems = [stem for stem in stems if not is_unwanted(stem)]
    onegram_list = [' '.join(ngram) for ngram in ngrams(stems, 1)]

    if 'mental' in onegram_list:
        print(text)


for i, row in df.iterrows():
    process_text(row['doc'])
