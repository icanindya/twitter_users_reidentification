import datetime
import time
import tweepy
import helper

mongo_client = helper.get_mongo_client()
twitter_db = mongo_client['twitter']
mytweets_col = twitter_db['my_tweets']

chosen_api = helper.get_twitter_app_apis()[0]

tweet_objs = chosen_api.user_timeline(screen_name='ic_anindya', count=200,
                                      trim_user=True, include_rts=False)

jsons = [tweet_obj._json for tweet_obj in tweet_objs]


mytweets_col.insert_many(jsons)
