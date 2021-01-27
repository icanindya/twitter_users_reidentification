import csv
import sys
from collections import defaultdict
from datetime import datetime, timedelta
import re

import helper

ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv'
ALL_TWEETS_PATH = r'E:\Data\AdversarialText\all_tweets_processed.csv'
ALL_TWEETS_CHUNKED_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets_chunked.csv'
YEARLY_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\yearly_tweets.csv'
X_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\x_tweets.csv'

CSV_HEADER = ['twitter_id', 'voter_serial', 'dob', 'age', 'sex', 'race',
              'zip', 'city', 'party', 'tweet_startdate', 'tweet_enddate',
              'num_tweets', 'num_hashtags', 'num_mentions', 'num_urls',
              'num_media', 'num_symbols', 'num_polls', 'text']

CSV_HEADER_CHUNKED = ['twitter_id', 'voter_serial', 'dob', 'age', 'sex', 'race',
                       'zip', 'city', 'party', 'tweet_startdate', 'tweet_enddate',
                       'num_tweets', 'num_hashtags', 'num_mentions', 'num_urls',
                       'num_media', 'num_symbols', 'num_polls', 'text25', 'text50',
                       'text75', 'text100', 'text125', 'textbeyond']

record = 0


def get_datetime(datetime_str):
    return datetime.strptime(datetime_str, '%a %b %d %H:%M:%S %z %Y')


def date_difference_days(datetime1, datetime2):
    return abs((datetime1 - datetime2).days)


def date_difference_years(datetime1, datetime2):
    return int(abs((datetime1 - datetime2).days) // 365.2425)


def get_age(begin_datetime, end_datetime, dob):
    days_in_window = date_difference_days(end_datetime, begin_datetime)
    middle_datetime = begin_datetime + timedelta(days=days_in_window // 2)
    dob_datetime = datetime.strptime(dob + ' -0500', '%m/%d/%Y %z')
    age = date_difference_years(middle_datetime, dob_datetime)
    return age


def get_csv_row(voter, tweet_obj_list, begin_index, end_index):
    begin_datetime = get_datetime(tweet_obj_list[begin_index]['created_at'])
    end_datetime = get_datetime(tweet_obj_list[end_index]['created_at'])

    voter['age'] = get_age(begin_datetime, end_datetime, voter['dob'])

    voter_attributes = [voter['twitter_id'], voter['serial'], voter['dob'],
                        voter['age'], voter['sex'], voter['race_code'],
                        voter['zip_code'], voter['city'], voter['party']]

    tweets = [x['text'].replace('\0', '') for x in tweet_obj_list[begin_index: end_index + 1]]

    eot_tweets = []

    for tweet in tweets:
        if tweet.endswith(('.', '!', '?')) is False:
            eot_tweets.append(tweet + '.')
        else:
            eot_tweets.append(tweet)

    text = ' '.join(eot_tweets)

    tweets_metadata = defaultdict(int)

    tweets_metadata['num_tweets'] = end_index - begin_index + 1

    for tweet_obj in tweet_obj_list[begin_index: end_index + 1]:

        if 'hashtags' in tweet_obj['entities']:
            tweets_metadata['num_hashtags'] += len(tweet_obj['entities']['hashtags'])

        if 'user_mentions' in tweet_obj['entities']:
            tweets_metadata['num_mentions'] += len(tweet_obj['entities']['user_mentions'])

        if 'urls' in tweet_obj['entities']:
            tweets_metadata['num_urls'] += len(tweet_obj['entities']['urls'])

        if 'media' in tweet_obj['entities']:
            tweets_metadata['num_media'] += len(tweet_obj['entities']['media'])

        if 'symbols' in tweet_obj['entities']:
            tweets_metadata['num_symbols'] += len(tweet_obj['entities']['symbols'])

        if 'polls' in tweet_obj['entities']:
            tweets_metadata['num_polls'] += len(tweet_obj['entities']['polls'])

    tweet_startdate = begin_datetime.strftime('%m/%d/%Y')
    tweet_enddate = end_datetime.strftime('%m/%d/%Y')

    tweets_attributes = [tweet_startdate, tweet_enddate,
                         str(tweets_metadata['num_tweets']), str(tweets_metadata['num_hashtags']),
                         str(tweets_metadata['num_mentions']), str(tweets_metadata['num_urls']),
                         str(tweets_metadata['num_media']), str(tweets_metadata['num_symbols']),
                         str(tweets_metadata['num_polls']), text]

    csv_record = voter_attributes + tweets_attributes

    global record
    record += 1
    if record % 100 == 0:
        print('record {}'.format(record))

    return csv_record

def get_csv_row_processed(voter, tweet_obj_list, begin_index, end_index):
    begin_datetime = get_datetime(tweet_obj_list[begin_index]['created_at'])
    end_datetime = get_datetime(tweet_obj_list[end_index]['created_at'])

    voter['age'] = get_age(begin_datetime, end_datetime, voter['dob'])

    voter_attributes = [voter['twitter_id'], voter['serial'], voter['dob'],
                        voter['age'], voter['sex'], voter['race_code'],
                        voter['zip_code'], voter['city'], voter['party']]

    tweets = [x['text'].replace('\0', '') for x in tweet_obj_list[begin_index: end_index + 1]]

    eot_tweets = []

    for tweet in tweets:
        lines = tweet.splitlines()
        eol_lines = []
        for line in lines:
            if line:
                changed_line = line.strip()
                if changed_line.endswith(('.', '!', '?')) is False:
                    eol_lines.append(changed_line + '.')
                else:
                    eol_lines.append(changed_line)

        eot_tweets.append(' '.join(eol_lines))

    text = ' '.join(eot_tweets)

    tweets_metadata = defaultdict(int)

    tweets_metadata['num_tweets'] = end_index - begin_index + 1

    for tweet_obj in tweet_obj_list[begin_index: end_index + 1]:

        if 'hashtags' in tweet_obj['entities']:
            tweets_metadata['num_hashtags'] += len(tweet_obj['entities']['hashtags'])

        if 'user_mentions' in tweet_obj['entities']:
            tweets_metadata['num_mentions'] += len(tweet_obj['entities']['user_mentions'])

        if 'urls' in tweet_obj['entities']:
            tweets_metadata['num_urls'] += len(tweet_obj['entities']['urls'])

        if 'media' in tweet_obj['entities']:
            tweets_metadata['num_media'] += len(tweet_obj['entities']['media'])

        if 'symbols' in tweet_obj['entities']:
            tweets_metadata['num_symbols'] += len(tweet_obj['entities']['symbols'])

        if 'polls' in tweet_obj['entities']:
            tweets_metadata['num_polls'] += len(tweet_obj['entities']['polls'])

    tweet_startdate = begin_datetime.strftime('%m/%d/%Y')
    tweet_enddate = end_datetime.strftime('%m/%d/%Y')

    tweets_attributes = [tweet_startdate, tweet_enddate,
                         str(tweets_metadata['num_tweets']), str(tweets_metadata['num_hashtags']),
                         str(tweets_metadata['num_mentions']), str(tweets_metadata['num_urls']),
                         str(tweets_metadata['num_media']), str(tweets_metadata['num_symbols']),
                         str(tweets_metadata['num_polls']), text]

    csv_record = voter_attributes + tweets_attributes

    global record
    record += 1
    if record % 100 == 0:
        print('record {}'.format(record))

    return csv_record


def get_csv_row_chunked(voter, tweet_obj_list, begin_index, end_index):
    begin_datetime = get_datetime(tweet_obj_list[begin_index]['created_at'])
    end_datetime = get_datetime(tweet_obj_list[end_index]['created_at'])

    voter['age'] = get_age(begin_datetime, end_datetime, voter['dob'])

    voter_attributes = [voter['twitter_id'], voter['serial'], voter['dob'],
                        voter['age'], voter['sex'], voter['race_code'],
                        voter['zip_code'], voter['city'], voter['party']]

    tweets = [x['text'].replace('\0', '') for x in tweet_obj_list[begin_index: end_index + 1]]

    eot_tweets = []

    for tweet in tweets:
        if tweet.endswith(('.', '!', '?')) is False:
            eot_tweets.append(tweet + '.')
        else:
            eot_tweets.append(tweet)

    text25 = ' '.join(eot_tweets[:25])
    text50 = ' '.join(eot_tweets[25:50])
    text75 = ' '.join(eot_tweets[50:75])
    text100 = ' '.join(eot_tweets[75:100])
    text125 = ' '.join(eot_tweets[100:125])
    textbeyond = ' '.join(eot_tweets[125:])

    tweets_metadata = defaultdict(int)

    tweets_metadata['num_tweets'] = end_index - begin_index + 1

    for tweet_obj in tweet_obj_list[begin_index: end_index + 1]:

        if 'hashtags' in tweet_obj['entities']:
            tweets_metadata['num_hashtags'] += len(tweet_obj['entities']['hashtags'])

        if 'user_mentions' in tweet_obj['entities']:
            tweets_metadata['num_mentions'] += len(tweet_obj['entities']['user_mentions'])

        if 'urls' in tweet_obj['entities']:
            tweets_metadata['num_urls'] += len(tweet_obj['entities']['urls'])

        if 'media' in tweet_obj['entities']:
            tweets_metadata['num_media'] += len(tweet_obj['entities']['media'])

        if 'symbols' in tweet_obj['entities']:
            tweets_metadata['num_symbols'] += len(tweet_obj['entities']['symbols'])

        if 'polls' in tweet_obj['entities']:
            tweets_metadata['num_polls'] += len(tweet_obj['entities']['polls'])

    tweet_startdate = begin_datetime.strftime('%m/%d/%Y')
    tweet_enddate = end_datetime.strftime('%m/%d/%Y')

    tweets_attributes = [tweet_startdate, tweet_enddate,
                         str(tweets_metadata['num_tweets']), str(tweets_metadata['num_hashtags']),
                         str(tweets_metadata['num_mentions']), str(tweets_metadata['num_urls']),
                         str(tweets_metadata['num_media']), str(tweets_metadata['num_symbols']),
                         str(tweets_metadata['num_polls']), text25, text50, text75, text100, text125,
                         textbeyond]

    csv_record = voter_attributes + tweets_attributes

    global record
    record += 1
    if record % 100 == 0:
        print('record {}'.format(record))

    return csv_record


def gen_ds_all_tweets():
    mongo_client = helper.get_mongo_client()

    twitter_db = mongo_client['twitter']
    tweets_col = twitter_db['tweets']
    voters_col = twitter_db['voters']
    ground_truths_col = twitter_db['ground_truths']

    tuples = [(x['twitter_id'], x['voter_serial']) for x in ground_truths_col.find({})]

    with open(ALL_TWEETS_PATH, 'w', newline='', encoding='utf-8') as wf_csv:
        writer = csv.writer(wf_csv, delimiter=',')
        writer.writerow(CSV_HEADER)

        for twitter_id, voter_serial in tuples:

            voter = voters_col.find_one({'serial': voter_serial})
            voter['twitter_id'] = twitter_id

            tweet_objs = tweets_col.find({'user.id_str': twitter_id, 'retweeted_status': {'$exists': False}})
            tweet_obj_list = list(tweet_objs)

            if tweet_obj_list:
                writer.writerow(get_csv_row_processed(voter, tweet_obj_list, 0, len(tweet_obj_list) - 1))


def gen_ds_all_tweets_chunked():
    mongo_client = helper.get_mongo_client()

    twitter_db = mongo_client['twitter']
    tweets_col = twitter_db['tweets']
    voters_col = twitter_db['voters']
    ground_truths_col = twitter_db['ground_truths']

    tuples = [(x['twitter_id'], x['voter_serial']) for x in ground_truths_col.find({})]

    with open(ALL_TWEETS_CHUNKED_PATH, 'w', newline='', encoding='utf-8') as wf_csv:
        writer = csv.writer(wf_csv, delimiter=',')
        writer.writerow(CSV_HEADER_CHUNKED)

        for twitter_id, voter_serial in tuples:

            voter = voters_col.find_one({'serial': voter_serial})
            voter['twitter_id'] = twitter_id

            tweet_objs = tweets_col.find({'user.id_str': twitter_id, 'retweeted_status': {'$exists': False}})
            tweet_obj_list = list(tweet_objs)

            if tweet_obj_list:
                writer.writerow(get_csv_row_chunked(voter, tweet_obj_list, 0, len(tweet_obj_list) - 1))


def gen_ds_yearly_tweets():
    mongo_client = helper.get_mongo_client()

    twitter_db = mongo_client['twitter']
    tweets_col = twitter_db['tweets']
    voters_col = twitter_db['voters']
    ground_truths_col = twitter_db['ground_truths']

    tuples = [(x['twitter_id'], x['voter_serial']) for x in ground_truths_col.find({})]

    with open(YEARLY_TWEETS_PATH, 'w', newline='', encoding='utf-8') as wf_csv:
        writer = csv.writer(wf_csv, delimiter=',')
        writer.writerow(CSV_HEADER)

        for twitter_id, voter_serial in tuples:

            voter = voters_col.find_one({'serial': voter_serial})
            voter['twitter_id'] = twitter_id

            tweet_objs = tweets_col.find({'user.id_str': twitter_id, 'retweeted_status': {'$exists': False}}).sort(
                [('id', 1)])
            tweet_obj_list = list(tweet_objs)

            end_index = len(tweet_obj_list) - 1
            curr_index = end_index

            while curr_index >= 0:

                end_datetime = get_datetime(tweet_obj_list[end_index]['created_at'])
                curr_datetime = get_datetime(tweet_obj_list[curr_index]['created_at'])

                if date_difference_days(curr_datetime, end_datetime) <= 365:
                    if curr_index == 0:
                        writer.writerow(get_csv_row(voter, tweet_obj_list, curr_index, end_index))
                    curr_index -= 1
                else:
                    writer.writerow(get_csv_row(voter, tweet_obj_list, curr_index + 1, end_index))
                    end_index = curr_index


def gen_ds_x_tweets():
    mongo_client = helper.get_mongo_client()

    twitter_db = mongo_client['twitter']
    tweets_col = twitter_db['tweets']
    voters_col = twitter_db['voters']
    ground_truths_col = twitter_db['ground_truths']

    tuples = [(x['twitter_id'], x['voter_serial']) for x in ground_truths_col.find({})]

    with open(X_TWEETS_PATH, 'w', newline='', encoding='utf-8') as wf_csv:
        writer = csv.writer(wf_csv, delimiter=',')
        writer.writerow(CSV_HEADER)

        for twitter_id, voter_serial in tuples:

            voter = voters_col.find_one({'serial': voter_serial})
            voter['twitter_id'] = twitter_id

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
                            get_csv_row(voter, tweet_obj_list, begin_index, curr_index))
                        begin_index = curr_index


if __name__ == '__main__':

    option = sys.argv[1]

    if option == '1':
        gen_ds_all_tweets()
    elif option == '2':
        gen_ds_yearly_tweets()
    elif option == '3':
        gen_ds_x_tweets()
    elif option == '4':
        gen_ds_all_tweets_chunked()
    else:
        print('Valid options are 1, 2, 3, & 4.')
