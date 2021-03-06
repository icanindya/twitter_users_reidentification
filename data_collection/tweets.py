import datetime
import time
import tweepy
import helper


RATE_LIMIT = 1500
TIME_WINDOW = 900
api_count = 0
begin_timestamp = 0
end_timestamp = 0

ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\all_tweets\all_tweets.txt'
ALL_USERS_PATH = r'D:\Data\Linkage\FL\FL18\users\all_users.txt'


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


def insert_tweets(tweets_col, tweet_jsons):

    tweets_col.insert_many(tweet_jsons)


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

    apis = helper.get_twitter_app_apis()
    mongo_client = helper.get_mongo_client()
    twitter_db = mongo_client['twitter']
    tweets_col = twitter_db['new_tweets']
    gt_col = twitter_db['ground_truths']
    index_col = twitter_db['new_tweets_index']

    user_ids = []

    gts = gt_col.find({})
    for gt in gts:
        user_ids.append(gt['twitter_id'])

    user_ids.sort()

    index = get_index(index_col)
    position = index['position']
    max_tweet_id = index['max_tweet_id']

    with open(ALL_TWEETS_PATH, 'a', encoding='utf-8') as wf:

        curr_position = position - 1

        for user_id in user_ids[position:]:

            curr_position += 1

            first_call = True
            tweet_objs = []

            while first_call or len(tweet_objs) > 0:
                tweet_objs = get_tweets(apis, curr_position, user_id, max_tweet_id, True)
                first_call = False

                if tweet_objs:
                    tweet_jsons = [tweet_obj._json for tweet_obj in tweet_objs]
                    insert_tweets(tweets_col, tweet_jsons)

                    max_tweet_id = tweet_objs[-1].id - 1

                update_index(index_col, curr_position, max_tweet_id)

            max_tweet_id = 0

