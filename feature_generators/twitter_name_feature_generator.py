import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
import unidecode
import re

def preprocess_name(name):

    # Remove parethesized content
    name = name.replace(r'\(.*\)', '')

    # Convert accented characters
    name = unidecode.unidecode(name)

    # Replace '-', '_' and '.' with ' ':
    name = name.replace('-', ' ').replace('_', ' ').replace('.', ' ')

    # Remove non-alpha characters except spaces
    name = re.sub(r'[^a-zA-Z ]', '', name)

    # Make lower-case
    name = name.lower()

    # Remove prefix mr., mr , ms , ms., mrs., mrs , miss, sir, dr
    prefix_list = ['mr ', 'ms ', 'mrs ', 'miss ', 'sir ', 'dr ']

    for prefix in prefix_list:
        if name.startswith(prefix):
            name = name[len(prefix):]

    # Convert consecutive spaces into single space
    name = re.sub(' +', ' ', name)

    # Finally trim
    name = name.strip()

    return name

ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv'
NAME_HANDLE_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets_twitter_name_handle.csv'

df1 = pd.read_csv(ALL_TWEETS_PATH, header=0, usecols=['twitter_id'])
df2 = pd.read_csv(NAME_HANDLE_PATH, header=0, converters={'twitter_name': str,
                                                          'twitter_handle': str})


df = pd.concat([df1, df2], axis=1)

df['twitter_name'] = df['twitter_name'].apply(preprocess_name)

vect = CountVectorizer(analyzer='char', max_df=0.3, min_df=3, ngram_range=(2, 2), lowercase=False)
a = vect.fit_transform(df['twitter_name'])
print(len(vect.vocabulary_))

vect = CountVectorizer(analyzer='char', max_df=0.3, min_df=3, ngram_range=(3, 3), lowercase=False)
a = vect.fit_transform(df['twitter_name'])
print(len(vect.vocabulary_))

vect = CountVectorizer(analyzer='char', max_df=0.3, min_df=3, ngram_range=(4, 4), lowercase=False)
a = vect.fit_transform(df['twitter_name'])
print(len(vect.vocabulary_))