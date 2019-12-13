import pandas as pd
from sklearn.model_selection import train_test_split
import csv

ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv'
YEARLY_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\yearly_tweets.csv'
NUM_TWEETS = 100
CSV_HEADER = 'twitter_ids_{}_tweets'.format(NUM_TWEETS)
SELECTED_TWITTER_IDS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\twitter_ids_{}_tweets.csv'.format(NUM_TWEETS)

df = pd.read_csv(ALL_TWEETS_PATH, header=0, usecols=['twitter_id', 'num_tweets', 'sex', 'race_code', 'party', 'city'])

df = df.loc[(df['num_tweets'] >= NUM_TWEETS) & (df['sex'].isin(['M', 'F']))]

set1 = set(df.twitter_id.unique())

df = pd.read_csv(YEARLY_TWEETS_PATH, header=0, usecols=['twitter_id', 'num_tweets', 'sex', 'age'])

df = df.loc[(df['num_tweets'] >= NUM_TWEETS) & (df['sex'].isin(['M', 'F']))]

set2 = set(df.twitter_id.unique())

print(len(set1))
print(len(set2))

selected_twitter_ids = set1.intersection(set2)

print(len(selected_twitter_ids))

with open(SELECTED_TWITTER_IDS_PATH, 'w', newline='', encoding='utf-8') as wf_csv:
    writer = csv.writer(wf_csv, delimiter=',')
    writer.writerow([CSV_HEADER])
    for twitter_id in selected_twitter_ids:
        writer.writerow([twitter_id])


