import pandas as pd

NUM_TWEETS = 125
SELECTED_TWITTER_IDS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\twitter_ids_{}_tweets.csv'.format(NUM_TWEETS)
ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv'

df_ids = pd.read_csv(SELECTED_TWITTER_IDS_PATH, header=0)
selected_ids = df_ids['twitter_id'].tolist()
df = pd.read_csv(ALL_TWEETS_PATH, header=0, usecols=['twitter_id', 'num_tweets'])

df = df.loc[df['twitter_id'].isin(selected_ids)]

print(df.shape)
print(df['num_tweets'].mean())