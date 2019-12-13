import pandas as pd

NUM_TWEETS = 50
SELECTED_TWITTER_IDS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\twitter_ids_{}_tweets.csv'.format(NUM_TWEETS)

df = pd.read_csv(SELECTED_TWITTER_IDS_PATH, header=0)
test_ids_df = df.sample(frac=0.20, random_state=10)
test_ids = test_ids_df['twitter_ids'].tolist()
train_ids_df = df.drop(test_ids_df.index)
train_ids = train_ids_df['twitter_ids'].tolist()

print(train_ids[:10])
print(test_ids[:10])

df = pd.read_csv(r"D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv", header=0)
train_df = df.loc[df['twitter_id'].isin(train_ids)]
test_df = df.loc[df['twitter_id'].isin(test_ids)]

print(len(train_df))
print(len(test_df))

