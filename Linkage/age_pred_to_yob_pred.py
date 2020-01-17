import pandas as pd
import numpy as np
import helper
from datetime import datetime, timedelta


def date_difference_days(datetime1, datetime2):

    return abs((datetime1 - datetime2).days)


def get_yob(tweet_startdate, tweet_enddate, age_pred):

    begin_datetime = datetime.strptime(tweet_startdate, '%m/%d/%Y')
    end_datetime = datetime.strptime(tweet_enddate, '%m/%d/%Y')
    days_in_window = date_difference_days(end_datetime, begin_datetime)
    middle_datetime = begin_datetime + timedelta(days=days_in_window // 2)

    yob_range = ''

    if age_pred == '18-':
        birth_start = middle_datetime - timedelta(days=18 * 365.2425)
        yob_range = '{}-{}'.format(birth_start.year, 2019)

    elif age_pred == '19-22':
        birth_start = middle_datetime - timedelta(days=22 * 365.2425)
        birth_end = middle_datetime - timedelta(days=19 * 365.2425)
        yob_range = '{}-{}'.format(birth_start.year, birth_end.year)

    elif age_pred == '23-33':
        birth_start = middle_datetime - timedelta(days=33 * 365.2425)
        birth_end = middle_datetime - timedelta(days=23 * 365.2425)
        yob_range = '{}-{}'.format(birth_start.year, birth_end.year)

    elif age_pred == '34-45':
        birth_start = middle_datetime - timedelta(days=45 * 365.2425)
        birth_end = middle_datetime - timedelta(days=34 * 365.2425)
        yob_range = '{}-{}'.format(birth_start.year, birth_end.year)

    elif age_pred == '46+':
        birth_end = middle_datetime - timedelta(days=46 * 365.2425)
        yob_range = '{}-{}'.format(1900, birth_end.year)

    return yob_range


for age_grp in ['18-', '19-22', '23-33', '34-45', '46+']:
    get_yob('04/25/2016', '04/18/2017', age_grp)


NUM_TWEETS = 50
SELECTED_TWITTER_IDS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\twitter_ids_{}_tweets.csv'.format(NUM_TWEETS)
YEARLY_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\yearly_tweets.csv'

ids_df = pd.read_csv(SELECTED_TWITTER_IDS_PATH, header=0)
test_ids_df = ids_df.sample(frac=helper.test_percentage, random_state=helper.random_seed)
test_ids = test_ids_df['twitter_ids'].tolist()
train_ids_df = ids_df.drop(test_ids_df.index)
train_ids = train_ids_df['twitter_ids'].tolist()

df = pd.read_csv(YEARLY_TWEETS_PATH, header=0, usecols=['twitter_id', 'tweet_startdate', 'tweet_enddate'])

test_df = df.loc[df['twitter_id'].isin(test_ids)]
test_df.reset_index(drop=True, inplace=True)
print(len(test_df))

pred_df = pd.read_csv(r"D:\Data\Linkage\FL\FL18\results\predictions\age_neural-network_doc2vec.csv", header=0)
pred_df.reset_index(drop=True, inplace=True)
print(len(pred_df))

combined_df = pd.concat([test_df, pred_df], axis=1, ignore_index=True)
combined_df.columns = ['twitter_id', 'tweet_startdate', 'tweet_enddate', 'age_pred']

for i, row in combined_df.iterrows():

    combined_df.loc[i, 'yob_pred'] = get_yob(row['tweet_startdate'], row['tweet_enddate'], row['age_pred'])

print(combined_df)

yob_pred_dict = {}

for i, row in combined_df.iterrows():
    if row['twitter_id'] not in yob_pred_dict:
        yob_pred_dict[row['twitter_id']] = row['yob_pred']

with open(r'D:\Data\Linkage\FL\FL18\results\predictions\predicted_yob.txt', 'w') as wf:

    for twitter_id, yob_pred in yob_pred_dict.items():
        wf.write('{},{}\n'.format(twitter_id, yob_pred))










