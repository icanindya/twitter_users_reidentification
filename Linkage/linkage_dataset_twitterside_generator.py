import pandas as pd
import helper
import unidecode
import re

def preprocess_name(name, title=False):

    # Remove parethesized content
    name = name.replace(r'\(.*\)', '')

    # Convert accented characters
    name = unidecode.unidecode(name)

    # Replace '-', '_' and '.' with ' ':
    name = name.replace('-', ' ').replace('_', ' ').replace('.', ' ')

    # Remove non-alpha characters except spaces
    name = re.sub(r'[^a-zA-Z ]', '', name)

    # Make lower-case
    name = name.lower()

    # Remove prefix mr., mr , ms , ms., mrs., mrs , miss, sir, dr
    prefix_list = ['mr ', 'ms ', 'mrs ', 'miss ', 'sir ', 'dr ']

    for prefix in prefix_list:
        if name.startswith(prefix):
            name = name[len(prefix):]

    # Convert consecutive spaces into single space
    name = re.sub(' +', ' ', name)

    # Finally trim
    name = name.strip()

    # Optionally titlecase
    if title:

        name = name.title()

    return name

def preprocess_city(city):

    city = re.sub(r'\W+', '', city)
    city = city.lower()
    return city

LINKAGE_TWITTERSIDE_PATH = r"D:\Data\Linkage\FL\FL18\linkage\twitterside.csv"
ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv'
PRED_DOB_PATH = r"D:\Data\Linkage\FL\FL18\attributes\predictions\dob_nn_doc2vec.csv"
PRED_SEX_PATH = r"D:\Data\Linkage\FL\FL18\attributes\predictions\sex_nn_doc2vec-name_ngrams.csv"
PRED_RACE_PATH = r"D:\Data\Linkage\FL\FL18\attributes\predictions\race_nn_doc2vec.csv"
PRED_PARTY_PATH = r"D:\Data\Linkage\FL\FL18\attributes\predictions\party_nn_doc2vec.csv"

test_ids_df = pd.read_csv(PRED_DOB_PATH, header=0, usecols=['twitter_id'])
test_ids_df['twitter_id'] = test_ids_df['twitter_id'].astype(str)
pred_dob_df = pd.read_csv(PRED_DOB_PATH, header=0, usecols=['orig_dob', 'pred_dob'])
pred_sex_df = pd.read_csv(PRED_SEX_PATH, header=0, usecols=['orig_sex', 'pred_sex'])
pred_race_df = pd.read_csv(PRED_RACE_PATH, header=0, usecols=['orig_race', 'pred_race'])
pred_party_df = pd.read_csv(PRED_PARTY_PATH, header=0, usecols=['orig_party', 'pred_party'])

df_list = [test_ids_df, pred_dob_df, pred_sex_df, pred_race_df, pred_party_df]

combined_df = pd.concat(df_list, axis=1)

print(len(combined_df))
mongo_client = helper.get_mongo_client()
twitter_db = mongo_client['twitter']
truths_col = twitter_db['ground_truths']
users_col = twitter_db['users']
voters_col = twitter_db['voters']

test_twitter_ids = test_ids_df['twitter_id'].tolist()

voter_serial_dict = {}
truth_objs = truths_col.find({})

for truth_obj in truth_objs:
    twitter_id = truth_obj['twitter_id']
    if twitter_id in test_twitter_ids:
        voter_serial_dict[twitter_id] = truth_obj['voter_serial']

user_obj_dict = {}
user_objs = users_col.find({'id_str': {'$in': list(test_twitter_ids)}})

for user_obj in user_objs:
    twitter_id = user_obj['id_str']
    user_obj_dict[twitter_id] = user_obj

voter_obj_dict = {}
voter_objs = voters_col.find({'serial': {'$in': list(voter_serial_dict.values())}})

for voter_obj in voter_objs:
    voter_serial = voter_obj['serial']
    voter_obj_dict[voter_serial] = voter_obj

combined_df.rename(columns={'orig_dob': 'orig_gen', 'pred_dob': 'pred_gen'}, inplace=True)

combined_df['twitter_name'] = combined_df['twitter_id'].apply(lambda x: user_obj_dict[x]['name'])
combined_df['twitter_handle'] = combined_df['twitter_id'].apply(lambda x: user_obj_dict[x]['screen_name'])
combined_df['voter_serial'] = combined_df['twitter_id'].apply(lambda x: voter_serial_dict[x])
combined_df['orig_fname'] = combined_df['twitter_id'].apply(lambda x: voter_obj_dict[voter_serial_dict[x]]['fname'])
combined_df['orig_mname'] = combined_df['twitter_id'].apply(lambda x: voter_obj_dict[voter_serial_dict[x]]['mname'])
combined_df['orig_lname'] = combined_df['twitter_id'].apply(lambda x: voter_obj_dict[voter_serial_dict[x]]['lname'])
combined_df['orig_city'] = combined_df['twitter_id'].apply(lambda x: voter_obj_dict[voter_serial_dict[x]]['city'].upper())
combined_df['orig_county'] = combined_df['twitter_id'].apply(lambda x: voter_obj_dict[voter_serial_dict[x]]['county_code'].upper())
combined_df['orig_zip'] = combined_df['twitter_id'].apply(lambda x: voter_obj_dict[voter_serial_dict[x]]['zip_code'][:5])
combined_df['orig_dob'] = combined_df['twitter_id'].apply(lambda x: voter_obj_dict[voter_serial_dict[x]]['dob'])

combined_df = combined_df[['twitter_id', 'voter_serial', 'twitter_name', 'twitter_handle',
                           'pred_gen', 'pred_sex', 'pred_race', 'pred_party',
                           'orig_fname', 'orig_mname', 'orig_lname', 'orig_city',
                           'orig_county', 'orig_zip',
                           'orig_dob', 'orig_gen', 'orig_sex', 'orig_race', 'orig_party'
                           ]]

combined_df['twitter_name'] = combined_df['twitter_name'].apply(preprocess_name, args=(False,))
combined_df['twitter_handle'] = combined_df['twitter_handle'].apply(preprocess_name, args=(False,))
combined_df['orig_city'] = combined_df['orig_city'].apply(preprocess_city)
combined_df['orig_fname'] = combined_df['orig_fname'].apply(preprocess_name, args=(False,))
combined_df['orig_mname'] = combined_df['orig_mname'].apply(preprocess_name, args=(False,))
combined_df['orig_lname'] = combined_df['orig_lname'].apply(preprocess_name, args=(False,))

combined_df.to_csv(LINKAGE_TWITTERSIDE_PATH, index=False)