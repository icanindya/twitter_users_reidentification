import pandas as pd
import numpy as np
import helper


NUM_TWEETS = 50
SELECTED_TWITTER_IDS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\twitter_ids_{}_tweets.csv'.format(NUM_TWEETS)
YEARLY_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\yearly_tweets.csv'

ids_df = pd.read_csv(SELECTED_TWITTER_IDS_PATH, header=0)
test_ids_df = ids_df.sample(frac=helper.test_percentage, random_state=helper.random_seed)
test_ids = test_ids_df['twitter_ids'].tolist()
train_ids_df = ids_df.drop(test_ids_df.index)
train_ids = train_ids_df['twitter_ids'].tolist()

df = pd.read_csv(YEARLY_TWEETS_PATH, header=0, usecols=['twitter_id', 'age'])
df['age'] = df['age'].apply(helper.get_maif_age_label)

test_df = df.loc[df['twitter_id'].isin(test_ids)]
test_df.reset_index(drop=True, inplace=True)
print(len(test_df))

pred_df = pd.read_csv(r"D:\Data\Linkage\FL\FL18\results\predictions\age_neural-network_doc2vec.csv", header=0)
pred_df.reset_index(drop=True, inplace=True)
print(len(pred_df))

combined_df = pd.concat([test_df, pred_df], axis=1, ignore_index=True)
print(combined_df)