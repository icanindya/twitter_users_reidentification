import datetime
import time
import tweepy
import helper
import sys


RATE_LIMIT = 1500
TIME_WINDOW = 900
api_count = 0
begin_timestamp = 0
end_timestamp = 0

NET_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\all_tweets\network_tweets.txt'
NET_USERS_PATH = r'D:\Data\Linkage\FL\FL18\users\network_users.txt'


def update_index(index_col, position, max_tweet_id):

    query = index_col.find_one()
    newvalues = {'$set': {'position': position, 'max_tweet_id': max_tweet_id}}
    index_col.update_one(query, newvalues)


def get_index(index_col):

    index = index_col.find_one()

    if not index:
        index = {'position': 0, 'max_tweet_id': 0}
        index_col.insert_one(index)

    return index


def store_tweets(nettweets_col, tweet_jsons):

    nettweets_col.insert_many(tweet_jsons)


def get_tweets(apis, curr_position, user_id, max_tweet_id, include_rts):

    global RATE_LIMIT, TIME_WINDOW, api_count, begin_timestamp, end_timestamp

    tweet_objs = []

    error = True

    while error:

        chosen_api = apis[api_count % len(apis)]
        api_count += 1

        if api_count % (RATE_LIMIT * len(apis)) == 1:
            begin_timestamp = time.time()

        elif api_count % (RATE_LIMIT * len(apis)) == 0:
            end_timestamp = time.time()
            elapsed_seconds = end_timestamp - begin_timestamp
            if elapsed_seconds < TIME_WINDOW + 5:
                now = datetime.datetime.now()
                then = now + datetime.timedelta(seconds=TIME_WINDOW + 5 - elapsed_seconds)
                print('Going to sleep for {} second(s). Will resume at {}:{}:{}.'.format(
                    int(TIME_WINDOW + 5 - elapsed_seconds), then.hour, then.minute, then.second))
                time.sleep(TIME_WINDOW + 5 - elapsed_seconds)

        print('api count: {}, curr_position: {}, user_id: {}, max_tweet_id: {}'
              .format(api_count, curr_position, user_id, max_tweet_id))

        try:
            if max_tweet_id:
                tweet_objs = chosen_api.user_timeline(user_id=user_id, count=200,
                                                      max_id=max_tweet_id, trim_user=True,
                                                      include_rts=include_rts)
            else:
                tweet_objs = chosen_api.user_timeline(user_id=user_id, count=200,
                                                      trim_user=True, include_rts=include_rts)

            error = False

        except tweepy.TweepError as te:
            print('api error: {}'.format(te.reason))
            if 'Not authorized' in te.reason or 'page does not exist' in te.reason:
                error = False

    return tweet_objs


if __name__ == '__main__':

    mod = int(sys.argv[1])

    apis = helper.get_twitter_app_apis()
    apis = [api for i, api in enumerate(apis) if i % 5 == mod]

    mongo_client = helper.get_mongo_client()
    twitter_db = mongo_client['twitter']
    nettweets_col = twitter_db['net_tweets']
    index_col = twitter_db['net_tweets_index_{}'.format(mod)]

    user_ids = []

    with open(NET_USERS_PATH, 'r') as rf:
        for i, line in enumerate(rf):
            if (i <= 874580 or i > 3763778) and i % 5 == mod:
                user_ids.append(line.strip())

    index = get_index(index_col)
    position = index['position']
    max_tweet_id = index['max_tweet_id']

    with open(NET_TWEETS_PATH, 'a', encoding='utf-8') as wf:

        curr_position = position - 1

        for user_id in user_ids[position:]:

            curr_position += 1

            first_call = True
            tweet_objs = []

            # while first_call or len(tweet_objs) > 0:

            if max_tweet_id != 0:
                max_tweet_id = 0
                continue

            tweet_objs = get_tweets(apis, curr_position, user_id, max_tweet_id, False)
            first_call = False

            if tweet_objs:

                tweet_jsons = [tweet_obj._json for tweet_obj in tweet_objs if tweet_obj.retweeted is False]
                store_tweets(nettweets_col, tweet_jsons)

                # tweets = [tweet_obj.text for tweet_obj in tweet_objs if tweet_obj.retweeted is False]
                #
                # for tweet in tweets:
                #     if __name__ == '__main__':
                #         tweet = tweet.replace('\0', '')\
                #             .replace('\r\n', ' ')\
                #             .replace('\r', ' ')\
                #             .replace('\n', ' ')\
                #             .replace('\f', ' ')
                #
                #     wf.write('{}\n'.format(tweet))
                #
                # wf.flush()

                max_tweet_id = tweet_objs[-1].id - 1

                update_index(index_col, curr_position, max_tweet_id)

            max_tweet_id = 0

# position without json 874580