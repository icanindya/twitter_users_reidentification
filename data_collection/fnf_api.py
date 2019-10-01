'''
Collects follower and friend (following) IDs of a Twitter
user using Twitter API. 

Scales by using multiple Twitter App credentials.
'''

import datetime
import sys
import time

import tweepy
import twitter_credentials as tcred

import mongo_client as mc

RATE_LIMIT = 15
TIME_WINDOW = 15 * 60

api_count = 0
begin_timestamp = end_timestamp = None


def update_fnf5k_index(mongo_client, index_col_name, position):
    twitter_db = mongo_client['twitter']
    index_col = twitter_db[index_col_name]
    query = index_col.find_one()
    newvalues = {'$set': {'position': position}}
    index_col.update_one(query, newvalues)


def get_fnf5k_index(mongo_client, index_col_name):
    twitter_db = mongo_client['twitter']
    index_col = twitter_db[index_col_name]
    index = index_col.find_one({}, {'position': 1})
    if not index:
        position = -1
        index = {'position': position}
        index_col.insert_one(index)
    return index['position']


def store_fnf(mongo_client, main_col_name, user_id, f_ids):
    json = {'user_id': user_id, 'f_ids': f_ids}

    twitter_db = mongo_client['twitter']
    main_col = twitter_db[main_col_name]
    main_col.insert_one(json)


def get_fnf(apis, position, user_id):
    global RATE_LIMIT, TIME_WINDOW, api_count, begin_timestamp, end_timestamp

    f_ids = []

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
            print('position: {}, api count: {}, user id: {}'.format(position, api_count, user_id))

            if sys.argv[1] == 'followers':
                f_ids = chosen_api.followers_ids(user_id=user_id, stringify_ids=True, count=5000)

            elif sys.argv[1] == 'following':
                f_ids = chosen_api.friends_ids(user_id=user_id, stringify_ids=True, count=5000)

            error = False

        except tweepy.TweepError as te:
            print('error code: {}'.format(te.reason))
            if 'Not authorized' or 'page does not exists' in te.reason:
                break
            else:
                time.sleep(5)
    return f_ids


if __name__ == '__main__':

    api_count = 0

    mongo_client = mc.get()
    twitter_db = mongo_client['twitter']
    users_col = twitter_db['users']

    if sys.argv[1] == 'followers':
        user_ids = users_col.distinct('id_str', {'followers_count': {'$lt': 5001}, 'protected': False})
        main_col_name = 'followers5k'
        index_col_name = 'followers5k_index'
    elif sys.argv[1] == 'following':
        user_ids = users_col.distinct('id_str', {'friends_count': {'$lt': 5001}, 'protected': False})
        main_col_name = 'following5k'
        index_col_name = 'following5k_index'

    apis = []

    for ckey, cksec in zip(tcred.consumer_keys, tcred.consumer_key_secrets):
        auth = tweepy.AppAuthHandler(ckey, cksec)
        api = tweepy.API(auth)
        apis.append(api)

    RATE_LIMIT *= len(apis)

    prev_position = get_fnf5k_index(mongo_client, index_col_name)

    for position, user_id in enumerate(user_ids):
        if position <= prev_position:
            continue
        f_ids = get_fnf(apis, position, user_id)
        store_fnf(mongo_client, main_col_name, user_id, f_ids)
        update_fnf5k_index(mongo_client, index_col_name, position)
