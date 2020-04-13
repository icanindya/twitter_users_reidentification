import collections
import csv

import pandas as pd

import helper

COMMON = False
NAME_MATCH = False
ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv'
YEARLY_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\yearly_tweets.csv'
NUM_TWEETS = 50
CSV_HEADER = 'twitter_id'

SELECTED_TWITTER_IDS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\twitter_ids_{}_tweets.csv'.format(NUM_TWEETS)

df = pd.read_csv(ALL_TWEETS_PATH, header=0, usecols=['twitter_id', 'num_tweets', 'sex', 'race', 'party', 'city'])

df = df.loc[(df['num_tweets'] >= NUM_TWEETS) & (df['sex'].isin(['M', 'F']))]

selected_twitter_ids = list(df['twitter_id'].apply(str).unique())

print('num users dob', len(selected_twitter_ids))

mongo_client = helper.get_mongo_client()
twitter_db = mongo_client['twitter']
gt_col = twitter_db['ground_truths']
users_col = twitter_db['users']
voters_col = twitter_db['voters']

selected_gts = list(gt_col.find({'twitter_id': {'$in': selected_twitter_ids}}))

selected_twitter_ids_dup = [selected_gt['twitter_id'] for selected_gt in selected_gts]

selected_vsers = [selected_gt['voter_serial'] for selected_gt in selected_gts]

twitter_id_counts = collections.Counter(selected_twitter_ids_dup)

selected_twitter_ids = [id for id in twitter_id_counts if twitter_id_counts[id] == 1]

print('num users unique dob', len(selected_twitter_ids))

if NAME_MATCH:

    selected_users = users_col.find({'id_str': {'$in': selected_twitter_ids}}, {'id_str': 1, 'name': 1})

    selected_voters = voters_col.find({'serial': {'$in': selected_vsers}},
                                      {'serial': 1, 'fname': 1, 'mname': 1, 'lname': 1})

    selected_users_dict = {}

    selected_voters_dict = {}

    for selected_user in selected_users:
        selected_users_dict[selected_user['id_str']] = {'name': selected_user['name']}

    for selected_voter in selected_voters:
        selected_voters_dict[selected_voter['serial']] = {'fname': selected_voter['fname'],
                                                          'mname': selected_voter['mname'],
                                                          'lname': selected_voter['lname']}

    selected_twitter_ids = []

    for selected_gt in selected_gts:

        selected_gt_tid = selected_gt['twitter_id']

        selected_gt_vser = selected_gt['voter_serial']

        if selected_gt_tid not in selected_users_dict:
            continue

        uname = selected_users_dict[selected_gt_tid]['name']

        vnames = selected_voters_dict[selected_gt_vser]

        vfname, vmname, vlname = vnames['fname'], vnames['mname'], vnames['lname']

        uname_low = uname.strip().lower()

        vfmlname_low = ' '.join([part for part in [vfname, vmname, vlname] if part]).strip().lower()

        vflname_low = ' '.join([part for part in [vfname, vlname] if part]).strip().lower()

        print(uname_low, '|', vflname_low, '|', vfmlname_low)

        if uname_low == vfmlname_low or uname_low == vflname_low:
            selected_twitter_ids.append(selected_gt_tid)

    print('num users unique name match', len(selected_twitter_ids))

if COMMON:
    df = pd.read_csv(YEARLY_TWEETS_PATH, header=0, usecols=['twitter_id', 'num_tweets', 'sex', 'age'])

    df = df.loc[(df['num_tweets'] >= NUM_TWEETS) & (df['sex'].isin(['M', 'F']))]

    age_twitter_ids = list(df['twitter_id'].apply(str).unique())

    print('num users age', len(age_twitter_ids))

    selected_twitter_ids = list(set(selected_twitter_ids).intersection(set(age_twitter_ids)))

    print('num users unique common', len(selected_twitter_ids))

with open(SELECTED_TWITTER_IDS_PATH, 'w', newline='', encoding='utf-8') as wf_csv:
    writer = csv.writer(wf_csv, delimiter=',')
    writer.writerow([CSV_HEADER])
    for twitter_id in selected_twitter_ids:
        writer.writerow([twitter_id])
