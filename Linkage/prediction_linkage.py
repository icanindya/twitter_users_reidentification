import pandas as pd
import helper

NUM_TWEETS = 50
SELECTED_TWITTER_IDS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\twitter_ids_{}_tweets.csv'.format(NUM_TWEETS)
ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv'
YEARLY_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\yearly_tweets.csv'

attribute = 'age'

df_list = []

if attribute == 'age':
    dataset_path = YEARLY_TWEETS_PATH
    df = pd.read_csv(dataset_path, header=0, usecols=['twitter_id', attribute])
    df['age'] = df['age'].apply(helper.get_maif_age_label)
    df_list.append(df)
else:
    dataset_path = ALL_TWEETS_PATH
    df = pd.read_csv(dataset_path, header=0, usecols=['twitter_id', attribute])
    if attribute == 'race_code':
        df['race_code'] = df['race_code'].apply(helper.get_text_race_code)
    df_list.append(df)

df = pd.concat(df_list, axis=1)

ids_df = pd.read_csv(SELECTED_TWITTER_IDS_PATH, header=0)
test_ids_df = ids_df.sample(frac=helper.test_percentage, random_state=helper.random_seed)
test_ids = test_ids_df['twitter_ids'].tolist()
train_ids_df = ids_df.drop(test_ids_df.index)
train_ids = train_ids_df['twitter_ids'].tolist()

train_df = df.loc[df['twitter_id'].isin(train_ids)]
test_df = df.loc[df['twitter_id'].isin(test_ids)]

age_pred_df = pd.read_csv(r"D:\Data\Linkage\FL\FL18\predictions\age_neural-network_doc2vec.csv", header=0)

test_df.reset_index(drop=True, inplace=True)

# print(test_df)
# print(age_pred_df)
df = pd.concat([test_df, age_pred_df], axis=1)
# print(df)

df = df.groupby(['twitter_id']).agg(lambda x: x.value_counts().index[0])

print(df)


