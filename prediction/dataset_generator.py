import csv
import sys
from collections import defaultdict
from datetime import datetime, timedelta

from nltk.tokenize.casual import TweetTokenizer
from text_processing import FeatureExtractor

import helper

ALL_TWEETS_TOKENS_PATH = r'D:\Data\Linkage\FL\FL18\tweets\all_tweets_tokens.csv'
ALL_TWEETS_EXT_FEATURES_PATH = r'D:\Data\Linkage\FL\FL18\tweets\all_tweets_ext_features.csv'
ALL_TWEETS_COMBINED_PATH = r'D:\Data\Linkage\FL\FL18\tweets\all_tweets_combined.csv'

YEARLY_TWEETS_TOKENS_PATH = r'D:\Data\Linkage\FL\FL18\tweets\yearly_tweets_tokens.csv'
YEARLY_TWEETS_EXT_FEATURES_PATH = r'D:\Data\Linkage\FL\FL18\tweets\yearly_tweets_ext_features.csv'
YEARLY_TWEETS_COMBINED_PATH = r'D:\Data\Linkage\FL\FL18\tweets\yearly_tweets_combined.csv'

X_TWEETS_TOKENS_PATH = r'D:\Data\Linkage\FL\FL18\tweets\x_tweets_tokens.csv'
X_TWEETS_EXT_FEATURES_PATH = r'D:\Data\Linkage\FL\FL18\tweets\x_tweets_ext_features.csv'
X_TWEETS_COMBINED_PATH = r'D:\Data\Linkage\FL\FL18\tweets\x_tweets_combined.csv'

row = 0

tweet_tokenizer = TweetTokenizer(preserve_case=True, reduce_len=False, strip_handles=False)


def is_urllike(text):
    lower = text.lower()
    if lower.startswith('http://') or lower.startswith('https://'):
        return True
    else:
        return False


def get_datetime(datetime_str):
    return datetime.strptime(datetime_str, '%a %b %d %H:%M:%S %z %Y')


def date_difference_days(datetime1, datetime2):
    return (datetime1 - datetime2).days


def date_difference_years(datetime1, datetime2):
    return int((datetime1 - datetime2).days // 365.2425)


def get_age(tweet_obj_list, begin_index, end_index, dob):
    begin_datetime = get_datetime(tweet_obj_list[begin_index]['created_at'])
    end_datetime = get_datetime(tweet_obj_list[end_index]['created_at'])
    days_in_window = date_difference_days(end_datetime, begin_datetime)
    middle_datetime = begin_datetime + timedelta(days=days_in_window // 2)
    dob_datetime = datetime.strptime(dob + ' -0500', '%m/%d/%Y %z')
    age = date_difference_years(middle_datetime, dob_datetime)
    return age


def get_csv_row(twitter_id, tweet_obj_list, begin_index, end_index, voter, convert_dob, mode):
    tweets = list(map(lambda x: x['text'].replace('\0', ''), tweet_obj_list[begin_index: end_index + 1]))

    voter['dob_or_age'] = voter['dob']
    if convert_dob:
        voter['dob_or_age'] = get_age(tweet_obj_list, begin_index, end_index, voter['dob'])
    voter_attributes = [voter['dob_or_age'], voter['sex'], voter['race_code'], voter['zip_code'], voter['city'],
                        voter['party']]

    if mode == 0:
        doc = ' '.join(tweets)
        tokens = [token for token in tweet_tokenizer.tokenize(doc) if is_urllike(token) == False]
        token_elem = ' '.join(tokens)
        csv_row = [twitter_id, token_elem] + voter_attributes

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

        csv_row = [twitter_id] + fe.get_all_features() + voter_attributes

    if mode == 2:
        doc = ' '.join(tweets)
        csv_row = [twitter_id, doc] + voter_attributes

    global row
    row += 1
    if row % 100 == 0:
        print('row {}'.format(row))

    return csv_row


def ds_all_tweets(mode):
    count = 0

    if mode == 0:
        all_tweets_path = ALL_TWEETS_TOKENS_PATH
    elif mode == 1:
        all_tweets_path = ALL_TWEETS_EXT_FEATURES_PATH
    elif mode == 2:
        all_tweets_path = ALL_TWEETS_COMBINED_PATH

    mongo_client = helper.get_mongo_client()

    twitter_db = mongo_client['twitter']
    tweets_col = twitter_db['tweets']
    voters_col = twitter_db['voters']
    ground_truths_col = twitter_db['ground_truths']

    tuples = [(x['twitter_id'], x['voter_serial']) for x in ground_truths_col.find({})]

    with open(all_tweets_path, 'w', newline='', encoding='utf-8') as wf_csv:
        writer = csv.writer(wf_csv, delimiter=',')

        for twitter_id, voter_serial in tuples:

            voter = voters_col.find_one({'serial': voter_serial})

            tweet_objs = tweets_col.find({'user.id_str': twitter_id, 'retweeted_status': {'$exists': False}})
            tweet_obj_list = list(tweet_objs)

            if tweet_obj_list:
                writer.writerow(get_csv_row(twitter_id, tweet_obj_list, 0, len(tweet_obj_list) - 1, voter, False, mode))
                count += 1

    print('count: {}'.format(count))


def ds_yearly_tweets(mode):
    count = 0

    if mode == 0:
        yearly_tweets_path = YEARLY_TWEETS_TOKENS_PATH
    elif mode == 1:
        yearly_tweets_path = YEARLY_TWEETS_EXT_FEATURES_PATH
    elif mode == 2:
        yearly_tweets_path = YEARLY_TWEETS_COMBINED_PATH

    mongo_client = helper.get_mongo_client()

    twitter_db = mongo_client['twitter']
    tweets_col = twitter_db['tweets']
    voters_col = twitter_db['voters']
    ground_truths_col = twitter_db['ground_truths']

    tuples = [(x['twitter_id'], x['voter_serial']) for x in ground_truths_col.find({})]

    with open(yearly_tweets_path, 'w', newline='', encoding='utf-8') as wf_csv:
        writer = csv.writer(wf_csv, delimiter=',')

        for twitter_id, voter_serial in tuples:

            voter = voters_col.find_one({'serial': voter_serial})

            tweet_objs = tweets_col.find({'user.id_str': twitter_id, 'retweeted_status': {'$exists': False}})
            tweet_obj_list = list(tweet_objs)

            begin_index = 0
            curr_index = 0

            while curr_index < len(tweet_obj_list):

                begin_datetime = get_datetime(tweet_obj_list[begin_index]['created_at'])
                curr_datetime = get_datetime(tweet_obj_list[curr_index]['created_at'])

                if date_difference_days(curr_datetime, begin_datetime) <= 365:
                    if curr_index == len(tweet_obj_list) - 1:
                        writer.writerow(
                            get_csv_row(twitter_id, tweet_obj_list, begin_index, curr_index, voter, True, mode))
                        count += 1
                    curr_index += 1
                else:
                    writer.writerow(
                        get_csv_row(twitter_id, tweet_obj_list, begin_index, curr_index - 1, voter, True, mode))
                    count += 1
                    begin_index = curr_index

    print('count: {}'.format(count))


def ds_x_tweets(mode):
    if mode == 0:
        x_tweets_path = X_TWEETS_TOKENS_PATH
    elif mode == 1:
        x_tweets_path = X_TWEETS_EXT_FEATURES_PATH
    elif mode == 2:
        x_tweets_path = X_TWEETS_COMBINED_PATH

    mongo_client = helper.get_mongo_client()

    twitter_db = mongo_client['twitter']
    tweets_col = twitter_db['tweets']
    voters_col = twitter_db['voters']
    ground_truths_col = twitter_db['ground_truths']

    tuples = [(x['twitter_id'], x['voter_serial']) for x in ground_truths_col.find({})]

    with open(x_tweets_path, 'w', newline='', encoding='utf-8') as wf_csv:
        writer = csv.writer(wf_csv, delimiter=',')

        for twitter_id, voter_serial in tuples:

            voter = voters_col.find_one({'serial': voter_serial})

            tweet_objs = tweets_col.find({'user.id_str': twitter_id, 'retweeted_status': {'$exists': False}})
            tweet_obj_list = list(tweet_objs)

            begin_index = None
            begin_datetime = None

            for curr_index in range(len(tweet_obj_list)):

                if begin_index == None:
                    begin_index = curr_index
                    begin_datetime = get_datetime(tweet_obj_list[begin_index]['created_at'])
                else:
                    curr_datetime = get_datetime(tweet_obj_list[curr_index]['created_at'])
                    while date_difference_days(curr_datetime, begin_datetime) > 365:
                        begin_index += 1
                        begin_datetime = get_datetime(tweet_obj_list[begin_index]['created_at'])
                    if curr_index - begin_index == 49:
                        writer.writerow(
                            get_csv_row(twitter_id, tweet_obj_list, begin_index, curr_index, voter, True, mode))
                        begin_index = curr_index


if __name__ == '__main__':

    option = int(sys.argv[1])
    mode = int(sys.argv[2])

    if option == 0:
        ds_all_tweets(mode)
    elif option == 1:
        ds_yearly_tweets(mode)
    elif option == 2:
        ds_x_tweets(mode)
