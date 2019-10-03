import datetime
import time

import tweepy
import twitter_credentials as tcred
import json

import helper

RATE_LIMIT = 900
TIME_WINDOW = 900
api_count = 0
begin_timestamp = 0
end_timestamp = 0

TWEETS_ID_FILE = r'D:\Data\Linkage\Other Datasets\Age\Zhang_ICWSM_2016\tweetsID.txt'

THRESHOLD = 100000


def get_tweet_index(index_col):
    index = index_col.find_one({}, {'position': 1})
    if not index:
        position = 0
        index = {'position': position}
        index_col.insert_one(index)
    return index['position']


def update_tweet_index(index_col, position):
    query = index_col.find_one()
    newvalues = {'$set': {'position': position}}
    index_col.update_one(query, newvalues, upsert=True)


def store_tweets(tweets_col, tweet_objs):
    tweets_col.insert_many(tweet_objs)


def get_tweets(apis, tweet_ids):

    global RATE_LIMIT, TIME_WINDOW, api_count, begin_timestamp, end_timestamp

    tweet_objs = []

    error = True

    while error:

        chosen_api = apis[api_count % len(apis)]
        api_count += 1

        if api_count % RATE_LIMIT == 1:
            begin_timestamp = time.time()

        elif api_count % RATE_LIMIT == 0:
            end_timestamp = time.time()
            elapsed_seconds = end_timestamp - begin_timestamp
            if elapsed_seconds < TIME_WINDOW + 5:
                now = datetime.datetime.now()
                then = now + datetime.timedelta(seconds=TIME_WINDOW + 5 - elapsed_seconds)
                print('Going to sleep for {} second(s). Will resume at {}:{}:{}.'.format(
                    int(TIME_WINDOW + 5 - elapsed_seconds), then.hour, then.minute, then.second))
                time.sleep(TIME_WINDOW + 5 - elapsed_seconds)

        try:
            print('api count: {}'.format(api_count))
            status_list = chosen_api.statuses_lookup(tweet_ids, include_entities=True, trim_user=True)
            tweet_objs = [status._json for status in status_list]
            error = False

        except tweepy.TweepError as te:
            print('Going to sleep for 5 seconds. Tweepy error: {}'.format(te.reason))
            time.sleep(5)

    return tweet_objs


def insert_tweet_ids_in_db(mongo_client):

    count = 0

    tweet_id_buffer = []

    with open(TWEETS_ID_FILE, 'r') as rf:
        for line in rf:
            if line.startswith('%') is False:

                tweet_ids = line.strip().split(',')
                count += len(tweet_ids)

                tweet_id_buffer.extend(tweet_ids)

                if len(tweet_id_buffer) >= THRESHOLD:
                    json_list = [{'id': tweet_id} for tweet_id in tweet_id_buffer[:THRESHOLD]]

                    maif_db = mongo_client['maif_db']
                    tweet_ids_col = maif_db['tweet_ids']
                    tweet_ids_col.insert_many(json_list)

                    tweet_id_buffer = tweet_id_buffer[THRESHOLD:]

    json_list = [{'id': tweet_id} for tweet_id in tweet_id_buffer]

    maif_db = mongo_client['maif_db']
    tweet_ids_col = maif_db['tweet_ids']
    tweet_ids_col.insert_many(json_list)

    print('total tweets: {}'.format(count))


if __name__ == '__main__':

    apis = []

    for ckey, cksec, atok, atsec in zip(tcred.consumer_keys, tcred.consumer_key_secrets, tcred.access_tokens, tcred.access_token_secrets):
        auth = tweepy.OAuthHandler(ckey, cksec)
        auth.set_access_token(atok, atsec)
        api = tweepy.API(auth)
        apis.append(api)

    mongo_client = helper.get_mongo_client()

    maif_db = mongo_client['maif_db']
    tweet_ids_col = maif_db['tweet_ids']
    tweets_col = maif_db['tweets']
    index_col = maif_db['tweet_id_index']

    tweet_id_index_obj = index_col.find()

    position = 0

    position = get_tweet_index(index_col)

    while True:

        tweet_id_buffer = [x['id'] for x in tweet_ids_col.find().limit(THRESHOLD * 10).skip(position)]

        if len(tweet_id_buffer) == 0:
            break

        while tweet_id_buffer:

            tweet_ids = tweet_id_buffer[:100]

            # print(position, len(tweet_ids), tweet_ids[0], tweet_ids[-1])

            tweet_objs = get_tweets(apis, tweet_ids)

            if tweet_objs:
                store_tweets(tweets_col, tweet_objs)

            tweet_id_buffer = tweet_id_buffer[len(tweet_ids):]

            position += len(tweet_ids)

            update_tweet_index(index_col, position)













