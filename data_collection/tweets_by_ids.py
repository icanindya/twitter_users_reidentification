import datetime
import time

import tweepy
import twitter_credentials as tcred

RATE_LIMIT = 900
TIME_WINDOW = 900


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

            tweet_objs = chosen_api.statuses_lookup(tweet_ids)

            error = False

        except tweepy.TweepError as te:
            print('error code: {}'.format(te.reason))
            if 'Not authorized' or 'page does not exists' in te.reason:
                break
            else:
                time.sleep(5)
    return tweet_objs


if __name__ == '__main__':
    # application-user authentication
    auth = tweepy.OAuthHandler(tcred.CONSUMER_KEY, tcred.CONSUMER_KEY_SECRET)
    auth.set_access_token(tcred.ACCESS_TOKEN, tcred.ACCESS_TOKEN_SECRET)
