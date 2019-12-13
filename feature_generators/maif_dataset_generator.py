import csv
import sys
import os
from collections import defaultdict
from datetime import datetime, timedelta

from nltk.tokenize.casual import TweetTokenizer
from text_processing import FeatureExtractor

import helper

ALL_TWEETS_TOKENS_PATH = r'D:\Data\Linkage\FL\FL18\tweets\maif_all_tweets_tokens.csv'
ALL_TWEETS_EXT_FEATURES_PATH = r'D:\Data\Linkage\FL\FL18\tweets\maif_all_tweets_ext_features.csv'
ALL_TWEETS_COMBINED_PATH = r'D:\Data\Linkage\FL\FL18\tweets\maif_all_tweets_combined.csv'

TOKENS_MODE = 0
EXT_FEATURES_MODE = 1
TWEETS_MODE = 2

row = 0

tweet_tokenizer = TweetTokenizer(preserve_case=True, reduce_len=False, strip_handles=False)


def insert_ages_in_db():

    mongo_client = helper.get_mongo_client()

    maif_db = mongo_client['maif_db']
    tweets_col = maif_db['tweets']
    age_labels_col = maif_db['age_labels']

    age_label_objs = []

    with open(r'D:\Data\Linkage\Other Datasets\Age\Zhang_ICWSM_2016\ageLabels.txt') as rf:
        for line in rf:
            tokens = line.strip().split(' ')
            id_str = tokens[0]
            age = tokens[1]
            age_label_obj = {'id_str': id_str, 'age': age}
            age_label_objs.append(age_label_obj)

    age_labels_col.insert_many(age_label_objs)


def is_urllike(text):
    lower = text.lower()
    if lower.startswith('http://') or lower.startswith('https://'):
        return True
    else:
        return False


def get_csv_row(twitter_id, tweet_obj_list, begin_index, end_index, age, mode=0):
    tweets = list(map(lambda x: x['text'].replace('\0', ''), tweet_obj_list[begin_index: end_index + 1]))

    if mode == 0:
        doc = ' '.join(tweets)
        tokens = [token for token in tweet_tokenizer.tokenize(doc) if is_urllike(token) is False]
        token_elem = ' '.join(tokens)
        csv_row = [twitter_id, token_elem, age]

    elif mode == 1:
        tweets_data = defaultdict(int)

        for tweet_obj in tweet_obj_list[begin_index: end_index + 1]:

            if 'hashtags' in tweet_obj['entities']:
                tweets_data['num_hashtags'] += len(tweet_obj['entities']['hashtags'])

            if 'user_mentions' in tweet_obj['entities']:
                tweets_data['num_mentions'] += len(tweet_obj['entities']['user_mentions'])

            if 'urls' in tweet_obj['entities']:
                tweets_data['num_urls'] += len(tweet_obj['entities']['urls'])

            if 'media' in tweet_obj['entities']:
                tweets_data['num_media'] += len(tweet_obj['entities']['media'])

            if 'symbols' in tweet_obj['entities']:
                tweets_data['num_symbols'] += len(tweet_obj['entities']['symbols'])

            if 'polls' in tweet_obj['entities']:
                tweets_data['num_polls'] += len(tweet_obj['entities']['polls'])

        fe = FeatureExtractor(tweets, tweets_data)

        csv_row = [twitter_id] + fe.get_all_features() + [age]

    if mode == 2:
        doc = ' '.join(tweets)
        csv_row = [twitter_id, doc, age]

    global row
    row += 1
    if row % 100 == 0:
        print('row {}'.format(row))

    return csv_row


def ds_all_tweets(mode):

    tweets_dist = {}

    count = 0

    mongo_client = helper.get_mongo_client()

    maif_db = mongo_client['maif_db']
    tweets_col = maif_db['tweets']
    age_labels_col = maif_db['age_labels']

    twitter_ids = tweets_col.distinct('user.id_str')

    if mode == TOKENS_MODE:
        all_tweets_path = ALL_TWEETS_TOKENS_PATH
    elif mode == EXT_FEATURES_MODE:
        all_tweets_path = ALL_TWEETS_EXT_FEATURES_PATH
    elif mode == TWEETS_MODE:
        all_tweets_path = ALL_TWEETS_COMBINED_PATH

    with open(all_tweets_path, 'w', newline='', encoding='utf-8') as wf_csv:
        writer = csv.writer(wf_csv, delimiter=',')

        for twitter_id in twitter_ids:

            age = age_labels_col.find_one({'id_str': twitter_id})['age']

            tweet_objs = tweets_col.find({'user.id_str': twitter_id})
            tweet_obj_list = list(tweet_objs)

            tweets_dist[twitter_id] = len(tweet_obj_list)

            if tweet_obj_list:
                writer.writerow(get_csv_row(twitter_id, tweet_obj_list, 0, len(tweet_obj_list) - 1, age, mode))
                count += 1

    print('count: {}'.format(count))

    with open(all_tweets_path + 'dist.txt', 'w') as wf:
        for k, v in tweets_dist.items():
            wf.write('{} {}\n'.format(k, v))


if __name__ == '__main__':

    ds_all_tweets(mode=TOKENS_MODE)
