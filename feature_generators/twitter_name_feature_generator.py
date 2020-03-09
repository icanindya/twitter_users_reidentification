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
twitter_name_path = file_name + '_twitter_name.csv'
twitter_handle_path = file_name + '_twitter_handle.csv'

def get_twitter_name(twitter_id):

    if twitter_id in user_obj_dict:
        return user_obj_dict[twitter_id]['name']
    else:
        print('user obj not avaialble', twitter_id)
        return '*'

def get_twitter_handle(twitter_id):

    if twitter_id in user_obj_dict:
        return user_obj_dict[twitter_id]['screen_name']
    else:
        return '*'

df = pd.read_csv(ALL_TWEETS_PATH, header=0, usecols=['twitter_id'])
twitter_id_list = df['twitter_id'] = df['twitter_id'].astype(str).tolist()

user_obj_dict = {}
user_objs = users_col.find({'id_str': {'$in': twitter_id_list}})

for user_obj in user_objs:
    user_obj_dict[user_obj['id_str']] = user_obj

df['twitter_name'] = df['twitter_id'].apply(get_twitter_name)
df['twitter_handle'] = df['twitter_id'].apply(get_twitter_handle)

df[['twitter_name']].to_csv(twitter_name_path, index=False)
df[['twitter_handle']].to_csv(twitter_handle_path, index=False)



