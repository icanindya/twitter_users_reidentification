import helper
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv'
YEARLY_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\yearly_tweets.csv'
NUM_TWEETS = 50
SELECTED_TWITTER_IDS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\twitter_ids_{}_tweets.csv'.format(NUM_TWEETS)

MIN = 0
MAX = 0

df = pd.read_csv(ALL_TWEETS_PATH, header=0)

ids_df = pd.read_csv(SELECTED_TWITTER_IDS_PATH, header=0)
test_ids_df = ids_df.sample(frac=helper.test_percentage, random_state=helper.random_seed)
test_ids = test_ids_df['twitter_ids'].tolist()
train_ids_df = ids_df.drop(test_ids_df.index)
train_ids = train_ids_df['twitter_ids'].tolist()

train_test_ids = train_ids + test_ids
train_test_df = df.loc[df['twitter_id'].isin(train_test_ids)]

tweet_counts = train_test_df['num_tweets'].value_counts().sort_index()

MIN = min(tweet_counts.index)
MAX - max(tweet_counts.index)

fig, axs = plt.subplots(1, 1, squeeze=False)

sns.barplot(tweet_counts.index, tweet_counts.values, ax=axs[0][0])
axs[0][0].set_ylabel('Num. of Occurances')
axs[0][0].set_xlabel('Num. of Tweets')
axs[0][0].set_xticklabels([str(x) if x in range(MIN, MAX + 1, 1000) else '' for x in range(MIN, MAX + 1)])
plt.show()

