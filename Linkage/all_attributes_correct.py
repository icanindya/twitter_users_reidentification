import pandas as pd
import helper

def get_yob_range(dob):

    yob = int(dob[-4:])

    if 2001 <= yob <= 2019:
        return '2001-2019'
    elif 1997 <= yob <= 2000:
        return '1997-2000'
    elif 1986 <= yob <= 1996:
        return '1986-1996'
    elif 1974 <= yob <= 1985:
        return '1974-1985'
    else:
        return '1900-1973'

mongo_client = helper.get_mongo_client()
twitter_db = mongo_client['twitter']

users_col = twitter_db['users']
truths_col = twitter_db['ground_truths']
voters_col = twitter_db['voters']

PRED_ALL_PATH = r"D:\Data\Linkage\FL\FL18\linkage\linkage_dataset_twitterside.csv"
PRED_NONE_PATH = r"D:\Data\Linkage\FL\FL18\linkage\linkage_dataset_twitterside_att.csv"

ds_twitter = pd.read_csv(PRED_ALL_PATH, header=0)

for i, row in ds_twitter.iterrows():

    voter_obj = voters_col.find_one({'serial': str(row['voter_serial'])})

    # ds_twitter.loc[i, 'twitter_name'] = voter_obj['fname'] + ' ' + voter_obj['lname']

    ds_twitter.loc[i, 'pred_sex'] = voter_obj['sex']
    ds_twitter.loc[i, 'pred_race'] = helper.get_short_race(int(voter_obj['race_code']))
    ds_twitter.loc[i, 'pred_yob'] = get_yob_range(voter_obj['dob'])
    ds_twitter.loc[i, 'pred_party'] = voter_obj['party']
    ds_twitter.loc[i, 'pred_city'] = voter_obj['city']

    # ds_twitter.loc[i, 'birthday'] = voter_obj['dob'][:-4]
    # ds_twitter.loc[i, 'city'] = voter_obj['city'].lower()

ds_twitter.to_csv(PRED_NONE_PATH, index=False)


