import os
import time
import tweepy
import twitter_credentials as tcred
import helper

LABEL_FILE_PATH = ''
RATE_LIMIT = 1500
TIME_WINDOW = 900
TW_ACCOUNTS_PARSED_DIR = r'D:\Data\Linkage\FL\FL18\tw_accounts_parsed_new'
NUM_FILES = 2000

api_count = 0
begin_timestamp = end_timestamp = None


def get_tweets(api, user_id, max_tweet_id):
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
        if max_tweet_id:
            tweets = api.user_timeline(user_id=user_id, count=200, max_id=max_tweet_id, trim_user=True,
                                       include_rts=True)
        else:
            tweets = api.user_timeline(user_id=user_id, count=200, trim_user=True, include_rts=True)
        return tweets
    except tweepy.TweepError as te:
        print('error code: {}'.format(te.reason))
        if 'Not authorized' in te.reason:
            return []
        else:
            return get_tweets(api, user_id, max_tweet_id)


def insert_user(col, json):
    twitter_db = mongo_client['twitter']
    users_col = twitter_db['users']
    users_col.insert_one(json)


def insert_tweets(mongo_client, json_list):
    twitter_db = mongo_client['twitter']
    tweets_col = twitter_db['tweets']
    tweets_col.insert_many(json_list)


def update_indices(mongo_client, user_id, max_tweet_id):
    twitter_db = mongo_client['twitter']
    indices_col = twitter_db['tweet_indices']
    query = indices_col.find_one()
    newvalues = {'$set': {'user_id': user_id, 'max_tweet_id': max_tweet_id}}
    indices_col.update_one(query, newvalues)


def get_indices(mongo_client):
    twitter_db = mongo_client['twitter']
    users_col = mongo_client['users']
    indices_col = twitter_db['tweet_indices']
    indices = indices_col.find_one()

    if not indices:
        indices = {'user_id': None, 'max_tweet_id': None}
        indices_col.insert_one(indices)
    return indices


def store_all_tweets(api, user_id, max_tweet_id):
    global api_count, begin_timestamp, end_timestamp
    tweets = []
    first_call = True

    while first_call or len(tweets) > 0:

        tweets = get_tweets(api, user_id, max_tweet_id)

        if first_call:
            first_call = False

        if tweets:
            #            print('tweets count: {}'.format(len(tweets)))
            json_list = [tweet._json for tweet in tweets]
            insert_tweets(mongo_client, json_list)
            max_tweet_id = tweets[-1].id - 1
            update_indices(mongo_client, user_id, max_tweet_id)


if __name__ == '__main__':

    # application-user authentication
    # auth = tweepy.OAuthHandler(tcred.CONSUMER_KEY, tcred.CONSUMER_KEY_SECRET)
    # auth.set_access_token(tcred.ACCESS_TOKEN, tcred.ACCESS_TOKEN_SECRET)

    # application-only authentication
    auth = tweepy.AppAuthHandler(tcred.CONSUMER_KEY, tcred.CONSUMER_KEY_SECRET)

    api = tweepy.API(auth)

    mongo_client = helper.get_mongo_client()

    indices = get_indices(mongo_client)
    last_user_id = indices['user_id']
    last_max_tweet_id = indices['max_tweet_id']

    #    store_all_tweets(api=api, user_id=896451334949527552, max_tweet_id=None)

    for file_id in range(NUM_FILES):
        file_path = os.path.join(TW_ACCOUNTS_PARSED_DIR, 'acc_parsed_{}.txt'.format(file_id))

        line_id = -1

        with open(file_path, 'r') as rf:
            for line in rf:
                line_id += 1
                tokens = list(map(lambda x: x.strip(), line.split('\t')))
                user_id = tokens[2]
                public_tweets = tokens[3] == 'T'

                print('file_id: {}, line_id: {}'.format(file_id, line_id))

                if last_user_id:
                    if user_id != last_user_id:
                        continue
                    else:
                        store_all_tweets(api, last_user_id, last_max_tweet_id)
                        last_user_id = None
                else:
                    if public_tweets:
                        store_all_tweets(api=api, user_id=user_id, max_tweet_id=None)
