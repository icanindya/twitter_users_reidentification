import os
import time
import urllib.parse
import pymongo
import tweepy
import twitter_credentials as tcred
import helper

RATE_LIMIT = 900
TIME_WINDOW = 900
TW_ACCOUNTS_PARSED_DIR = r'D:\Data\Linkage\FL\FL18\tw_accounts_parsed_new'
NUM_FILES = 2000

api_count = 0
begin_timestamp = None
end_timestamp = None


def get_users(api, user_ids, last_user_position):
    global api_count, begin_timestamp, end_timestamp

    api_count += 1
    print('api count: {}'.format(api_count))

    if api_count % RATE_LIMIT == 1:
        begin_timestamp = time.time()

    elif api_count % RATE_LIMIT == 0:
        end_timestamp = time.time()
        elapsed_seconds = end_timestamp - begin_timestamp
        if elapsed_seconds < TIME_WINDOW + 5:
            print('Going to sleep for {} second(s).'.format(int(TIME_WINDOW + 5 - elapsed_seconds)))
            time.sleep(TIME_WINDOW + 5 - elapsed_seconds)

    try:
        users = api.lookup_users(user_ids)
        return users
    except tweepy.TweepError as te:
        print('api error: {}'.format(te.reason))
        return get_users(api, user_ids, last_user_position)


def insert_users(mongo_client, json_list):
    twitter_db = mongo_client['twitter']
    users_col = twitter_db['users']
    users_col.insert_many(json_list)


def update_indices(mongo_client, last_user_position):
    twitter_db = mongo_client['twitter']
    indices_col = twitter_db['user_indices']
    query = indices_col.find_one()
    newvalues = {'$set': {'last_user_position': last_user_position}}
    indices_col.update_one(query, newvalues)


def get_indices(mongo_client):
    twitter_db = mongo_client['twitter']
    indices_col = twitter_db['user_indices']
    indices = indices_col.find_one()

    if not indices:
        indices = {'last_user_position': -1}
        indices_col.insert_one(indices)
    return indices


if __name__ == '__main__':

    # application-user authentication
    auth = tweepy.OAuthHandler(tcred.consumer_keys[0], tcred.consumer_key_secrets[0])
    auth.set_access_token(tcred.access_tokens[0], tcred.access_token_secrets[0])

    # application-only authentication
    # auth = tweepy.AppAuthHandler(tcred.CONSUMER_KEY, tcred.CONSUMER_KEY_SECRET)

    api = tweepy.API(auth)

    mongo_client = helper.get_mongo_client()

    user_ids = []
    indices = get_indices(mongo_client)
    last_user_position = indices['last_user_position']
    user_position = -1

    for file_id in range(NUM_FILES):
        file_path = os.path.join(TW_ACCOUNTS_PARSED_DIR, 'acc_parsed_{}.txt'.format(file_id))
        with open(file_path, 'r') as rf:
            for line in rf:
                user_position += 1
                tokens = list(map(lambda x: x.strip(), line.split('\t')))
                user_id = int(tokens[2])
                user_ids.append(user_id)

    curr_user_position = last_user_position + 1

    while curr_user_position < len(user_ids):
        print('curr user postion: {}'.format(curr_user_position))

        curr_user_ids = user_ids[curr_user_position:min(curr_user_position + 100, len(user_ids))]
        users = get_users(api, curr_user_ids, last_user_position)
        json_list = [user._json for user in users]
        insert_users(mongo_client, json_list)
        curr_user_position += len(curr_user_ids)
        update_indices(mongo_client, curr_user_position - 1)
