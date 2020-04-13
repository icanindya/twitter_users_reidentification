import pandas as pd
import csv
import sys
import os
import helper
mongo_client = helper.get_mongo_client()
twitter_db = mongo_client['twitter']
truths_col = twitter_db['ground_truths']
users_col = twitter_db['users']
voters_col = twitter_db['voters']

ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv'

file_name, file_ext = os.path.splitext(ALL_TWEETS_PATH)
twitter_name_handle_path = file_name + '_twitter_name_handle.csv'

df = pd.read_csv(ALL_TWEETS_PATH, header=0, usecols=['twitter_id'], converters={'twitter_id': str})
twitter_id_list = df['twitter_id'].tolist()

user_obj_dict = {}
user_objs = users_col.find({'id_str': {'$in': twitter_id_list}})

for user_obj in user_objs:
    user_obj_dict[user_obj['id_str']] = user_obj

df['twitter_name'] = df['twitter_id'].apply(lambda x: user_obj_dict[x]['name'])
df['twitter_handle'] = df['twitter_id'].apply(lambda x: user_obj_dict[x]['screen_name'])

df.to_csv(twitter_name_handle_path, columns=['twitter_name', 'twitter_handle'], index=False)



