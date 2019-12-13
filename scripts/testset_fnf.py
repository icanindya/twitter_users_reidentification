import helper
import pandas as pd

NUM_TWEETS = 50
SELECTED_TWITTER_IDS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\twitter_ids_{}_tweets.csv'.format(NUM_TWEETS)

ids_df = pd.read_csv(SELECTED_TWITTER_IDS_PATH, header=0)
test_ids_df = ids_df.sample(frac=helper.test_percentage, random_state=helper.random_seed)
test_ids = test_ids_df['twitter_ids'].tolist()

mongo_client = helper.get_mongo_client()

twitter_db = mongo_client['twitter']
users_col = twitter_db['users']
followers_col = twitter_db['followers5k']
following_col = twitter_db['following5k']
net_users_col = twitter_db['users']

network_ids = set()

for i, user_id in enumerate(test_ids):
    follower_obj = followers_col.find_one({'user_id': str(user_id)})
    if follower_obj is not None:
        follower_ids = follower_obj['f_ids']
    following_obj = following_col.find_one({'user_id': str(user_id)})
    if following_obj is not None:
        following_ids = following_obj['f_ids']
    fnf_ids = follower_ids + following_ids
    network_ids.update(fnf_ids)

    if i % 100 == 0:
        print(i, len(network_ids))

with open(r'D:\test_network_ids.txt', 'w') as wf:
    for network_id in network_ids:
        wf.write('{}\n'.format(network_id))




