import pandas as pd
import helper

mongo_client = helper.get_mongo_client()
twitter_db = mongo_client['twitter']
users_col = twitter_db['users']
gt_col = twitter_db['ground_truths']

voter_serial_dict = {}
gt_objs = gt_col.find({})

for gt_obj in gt_objs:
    voter_serial_dict[gt_obj['twitter_id']] = gt_obj['voter_serial']

PRED_ALL_PATH = r"D:\Data\Linkage\FL\FL18\results\linkage\linkage_dataset_twitterside.csv"
PRED_DOB_PATH = r"D:\Data\Linkage\FL\FL18\results\predictions\predicted_dob.txt"
pred_dob_dict = {}

with open(PRED_DOB_PATH, 'r') as rf:
    for line in rf:
        tokens = line.strip().split(',')
        pred_dob_dict[tokens[0]] = tokens[1]

NUM_TWEETS = 50
SELECTED_TWITTER_IDS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\twitter_ids_{}_tweets.csv'.format(NUM_TWEETS)
ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv'
PRED_RACE_PATH = r"D:\Data\Linkage\FL\FL18\results\predictions\race_neural-network_doc2vec.csv"
PRED_SEX_PATH = r"D:\Data\Linkage\FL\FL18\results\predictions\sex_neural-network_doc2vec.csv"
PRED_PARTY_PATH = r"D:\Data\Linkage\FL\FL18\results\predictions\party_neural-network_doc2vec.csv"
PRED_AGE_PATH = r"D:\Data\Linkage\FL\FL18\results\predictions\predicted_dob.txt"

ids_df = pd.read_csv(SELECTED_TWITTER_IDS_PATH, header=0)
test_ids_df = ids_df.sample(frac=helper.test_percentage, random_state=helper.random_seed)
test_ids = test_ids_df['twitter_ids'].tolist()
train_ids_df = ids_df.drop(test_ids_df.index)
train_ids = train_ids_df['twitter_ids'].tolist()

df = pd.read_csv(ALL_TWEETS_PATH, header=0, usecols=['twitter_id'])

test_df = df.loc[df['twitter_id'].isin(test_ids)]
test_df.reset_index(drop=True, inplace=True)

pred_party_df = pd.read_csv(PRED_PARTY_PATH, header=0)
pred_race_df = pd.read_csv(PRED_RACE_PATH, header=0)
pred_sex_df = pd.read_csv(PRED_SEX_PATH, header=0)

df_list = [test_df, pred_sex_df, pred_race_df, pred_party_df]

combined_df = pd.concat(df_list, axis=1)
combined_df.columns = ['twitter_id', 'pred_sex', 'pred_race', 'pred_party']

for i, row in combined_df.iterrows():
    twitter_id = str(row['twitter_id'])
    user_obj = users_col.find_one({'id_str': twitter_id})
    combined_df.loc[i, 'pred_dob'] = pred_dob_dict[twitter_id]
    combined_df.loc[i, 'twitter_name'] = user_obj['name']
    combined_df.loc[i, 'twitter_handle'] = user_obj['screen_name']
    combined_df.loc[i, 'voter_serial'] = voter_serial_dict[twitter_id]

combined_df = combined_df[['twitter_id', 'voter_serial', 'twitter_name', 'twitter_handle', 'pred_sex', 'pred_race', 'pred_yob', 'pred_party']]

combined_df.to_csv(PRED_ALL_PATH, index=False)